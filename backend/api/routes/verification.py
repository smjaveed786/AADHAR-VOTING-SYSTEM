"""
Verification API Routes

Endpoints:
- POST /api/verify/liveness - Process video frames for liveness detection
- POST /api/verify/face - Compare face embedding with database
- POST /api/verify/complete - Combined verification returning voting token

This implements the dual-layer security:
1. Liveness Detection - Verify real person (not photo/video)
2. Face Recognition - Match with registered embedding
"""

import base64
from datetime import datetime
from typing import List, Optional
import uuid

from fastapi import APIRouter, HTTPException, status, UploadFile, File, Form
from pydantic import BaseModel

from settings import get_settings


from services.liveness_service import liveness_service
from services.face_service import face_service
import json
import numpy as np
import os


router = APIRouter()


# ============================================
# REQUEST/RESPONSE MODELS
# ============================================

class LivenessRequest(BaseModel):
    """Request for liveness detection."""
    # Frames as base64 encoded images
    frames: List[str]


class LivenessResponse(BaseModel):
    """Liveness detection result."""
    verdict: str  # "LIVE" or "SPOOF"
    confidence: float
    message: str


class FaceVerificationRequest(BaseModel):
    """Request for face verification."""
    aadhaar_number: str
    # Face image as base64 encoded string
    image: str


class FaceVerificationResponse(BaseModel):
    """Face verification result."""
    matched: bool
    similarity: float
    voter_id: Optional[str] = None
    constituency_no: Optional[int] = None
    message: str


class CompleteVerificationRequest(BaseModel):
    """Request for complete verification (liveness + face)."""
    aadhaar_number: str
    # Frames for liveness detection
    frames: List[str]


class VotingToken(BaseModel):
    """Token issued after successful verification."""
    token: str
    voter_id: str
    constituency_no: int
    expires_at: datetime
    message: str


class VerificationFailure(BaseModel):
    """Verification failure response."""
    success: bool = False
    stage: str  # "liveness" or "face"
    message: str


# ============================================
# ROUTES
# ============================================

@router.post("/liveness", response_model=LivenessResponse)
async def check_liveness(request: LivenessRequest):
    """
    Perform liveness detection on video frames.
    
    Accepts a list of base64-encoded video frames (recommended: 30 frames at 1 FPS).
    Uses the trained liveness detection model to determine if the subject is a
    real person or a spoof (photo, video, mask).
    
    Returns:
    - verdict: "LIVE" or "SPOOF"
    - confidence: Model confidence (0-1)
    - message: Human-readable result
    
    Implementation uses: models/liveness_detector_production.pth
    """
    if len(request.frames) < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one frame is required"
        )
    
    # Run liveness detection on frames
    result = liveness_service.predict_from_base64_frames(request.frames)
    
    return LivenessResponse(
        verdict=result["verdict"],
        confidence=result["confidence"],
        message=result.get("message", "Liveness check completed")
    )


@router.post("/face", response_model=FaceVerificationResponse)
async def verify_face(request: FaceVerificationRequest):
    """
    Verify face against registered embedding.
    
    Accepts:
    - aadhaar_number: Voter's Aadhaar number
    - image: Base64-encoded face image
    
    Process:
    1. Look up registered embedding by Aadhaar number
    2. Extract embedding from provided image using InsightFace
    3. Compute cosine similarity
    4. Return match result based on threshold
    
    Threshold: 0.5 (configurable in settings)
    """
    settings = get_settings()
    
    # Validate Aadhaar
    if len(request.aadhaar_number) != 12 or not request.aadhaar_number.isdigit():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Aadhaar number"
        )
    
    # 1. Look up voter in JSON DB
    settings = get_settings()
    voters_file = settings.base_dir.parent / "data" / "voters.json"
    
    if not voters_file.exists():
         raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Voter database not found"
        )
    
    try:
        with open(voters_file, 'r') as f:
            voters_db = json.load(f)
    except:
        voters_db = {}
        
    voter_info = voters_db.get(request.aadhaar_number)
    
    if not voter_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Voter not found with this Aadhaar number"
        )
        
    voter_id = voter_info["voter_id"]
    constituency_no = voter_info["constituency_no"]
    
    # 2. Load registered embedding
    save_dir = settings.base_dir.parent / "data" / "registered_faces"
    embedding_path = save_dir / f"{voter_id}.npy"
    
    if not embedding_path.exists():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Biometric data not found for this voter"
        )
        
    try:
        registered_embedding = np.load(embedding_path)
    except Exception as e:
         raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error loading biometric data: {e}"
        )
        
    # 3. Extract embedding from input image
    live_embedding = face_service.generate_embedding_from_base64(request.image)
    
    if live_embedding is None:
        return FaceVerificationResponse(
            matched=False,
            similarity=0.0,
            message="No face detected in live image"
        )
        
    # 4. Compare embeddings
    similarity, is_match = face_service.compare_embeddings(
        registered_embedding, 
        live_embedding, 
        threshold=settings.face_similarity_threshold
    )
    
    return FaceVerificationResponse(
        matched=is_match,
        similarity=similarity,
        voter_id=voter_id if is_match else None,
        constituency_no=constituency_no if is_match else None,
        message=f"Verification {'successful' if is_match else 'failed'}. Similarity: {similarity:.2f}"
    )


@router.post("/complete")
async def complete_verification(request: CompleteVerificationRequest):
    """
    Perform complete dual-layer verification.
    
    This is the main verification endpoint that:
    1. Runs liveness detection on provided frames
    2. If LIVE, extracts face embedding from best frame
    3. Matches face with registered embedding
    4. If matched, issues a voting token
    
    Returns either:
    - VotingToken (on success)
    - VerificationFailure (on failure)
    
    The voting token must be used within 5 minutes.
    """
    # Validate Aadhaar
    if len(request.aadhaar_number) != 12 or not request.aadhaar_number.isdigit():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Aadhaar number"
        )
    
    if len(request.frames) < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least 1 frame required for liveness detection"
        )
    
    # Step 1: Liveness Detection
    liveness_result = liveness_service.predict_from_base64_frames(request.frames)
    
    # Log liveness result for debugging
    print(f"🔍 Liveness Result: verdict={liveness_result['verdict']}, confidence={liveness_result.get('confidence', 0):.2f}")
    print(f"   Live frames: {liveness_result.get('live_count', 0)}, Spoof frames: {liveness_result.get('spoof_count', 0)}")
    
    if liveness_result["verdict"] == "SPOOF":
        return {
            "success": False,
            "stage": "liveness",
            "message": f"Liveness check failed. Spoof detected with {liveness_result['confidence']*100:.1f}% confidence."
        }
    
    # Step 2: Face Recognition
    # Look up voter
    settings = get_settings()
    voters_file = settings.base_dir.parent / "data" / "voters.json"
    
    if not voters_file.exists():
         raise HTTPException(status_code=404, detail="Voter database not found")
            
    with open(voters_file, 'r') as f:
        voters_db = json.load(f)
        
    voter_info = voters_db.get(request.aadhaar_number)
    
    if not voter_info:
        raise HTTPException(status_code=404, detail="Voter not registered")
        
    # Check if already voted
    if voter_info.get("has_voted", False):
        voted_at = voter_info.get("voted_at", "")
        return {
            "success": False,
            "stage": "already_voted",
            "message": "You have already cast your vote.",
            "voted_at": voted_at
        }
    
    # Load registered embedding
    save_dir = settings.base_dir.parent / "data" / "registered_faces"
    embedding_path = save_dir / f"{voter_info['voter_id']}.npy"
    
    try:
        registered_embedding = np.load(embedding_path)
    except:
        return {
            "success": False,
            "stage": "face",
            "message": "Biometric data corrupted or missing."
        }
    
    # Extract embedding from best frame (using first frame for now)
    # Ideally, we should pick the frame with best face score
    # For now, try the first frame, if fails, try others?
    best_similarity = 0.0
    matched = False
    
    # Try up to 3 frames to find a match
    for frame_b64 in request.frames[:3]:
        live_embedding = face_service.generate_embedding_from_base64(frame_b64)
        if live_embedding is not None:
            sim, is_match = face_service.compare_embeddings(
                registered_embedding, 
                live_embedding, 
                threshold=settings.face_similarity_threshold
            )
            if sim > best_similarity:
                best_similarity = sim
            if is_match:
                matched = True
                break
    
    if not matched:
        return {
            "success": False,
            "stage": "face",
            "message": f"Face verification failed. Best similarity: {best_similarity:.2f}"
        }
    
    # Step 4: Issue Voting Token
    from datetime import timedelta, timezone
    
    token = uuid.uuid4().hex
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=5)
    
    # Save token mapping (in memory or file) logic if needed, 
    # but for now token validation in voting.py is placeholder anyway.
    
    return {
        "success": True,
        "token": token,
        "voter_id": voter_info["voter_id"],
        "constituency_no": voter_info["constituency_no"],
        "expires_at": expires_at.isoformat(),
        "message": "Verification successful. You have 5 minutes to cast your vote."
    }
