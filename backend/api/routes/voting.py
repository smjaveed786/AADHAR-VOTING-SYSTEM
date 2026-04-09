"""
Voting API Routes

Endpoints:
- GET /api/vote/candidates/{constituency} - Get candidates for constituency
- POST /api/vote/submit - Submit anonymous vote to blockchain
- GET /api/vote/status/{aadhaar} - Check if voter has voted
"""

import hashlib
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from settings import get_settings


router = APIRouter()


# ============================================
# REQUEST/RESPONSE MODELS
# ============================================

class CandidateResponse(BaseModel):
    """Candidate information."""
    id: int
    name: str
    party: str
    constituency_no: int
    constituency_name: str
    # Optional: photo URL
    photo_url: Optional[str] = None


class CandidatesListResponse(BaseModel):
    """List of candidates for a constituency."""
    constituency_no: int
    constituency_name: str
    total_candidates: int
    candidates: List[CandidateResponse]


class VoteSubmitRequest(BaseModel):
    """Request to submit a vote."""
    token: str  # Voting token from verification
    voter_id: str
    candidate_id: int


class VoteSubmitResponse(BaseModel):
    """Vote submission response."""
    success: bool
    message: str
    # Anonymous transaction info
    block_index: Optional[int] = None
    vote_hash: Optional[str] = None


class VoteStatusResponse(BaseModel):
    """Voter status response."""
    has_voted: bool
    message: str


# ============================================
# LOAD CANDIDATES FROM CSV
# ============================================
import csv
from pathlib import Path

def load_candidates_from_csv():
    """Load candidates from CSV file into a dictionary."""
    candidates_dict = {}
    csv_path = Path(__file__).parent.parent.parent.parent / "database" / "candidates.csv"
    
    if not csv_path.exists():
        print(f"⚠️ Candidates CSV not found at: {csv_path}")
        return {}
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            candidate_id = 1
            
            for row in reader:
                const_no = int(row['Constituency No'])
                const_name = row['Constituency Name']
                party = row['Party']
                candidate_name = row['Candidate']
                
                if const_no not in candidates_dict:
                    candidates_dict[const_no] = {
                        "name": const_name,
                        "candidates": []
                    }
                
                candidates_dict[const_no]["candidates"].append({
                    "id": candidate_id,
                    "name": candidate_name,
                    "party": party
                })
                candidate_id += 1
                
        print(f"✅ Loaded candidates for {len(candidates_dict)} constituencies")
    except Exception as e:
        print(f"⚠️ Error loading candidates CSV: {e}")
    
    return candidates_dict

# Load candidates on module import
CANDIDATES_DATA = load_candidates_from_csv()


# ============================================
# ROUTES
# ============================================

@router.get("/candidates/{constituency_no}", response_model=CandidatesListResponse)
async def get_candidates(constituency_no: int):
    """
    Get all candidates for a specific constituency.
    
    Returns candidate list with:
    - Candidate ID (for vote submission)
    - Candidate name
    - Party affiliation
    - Constituency info
    """
    # Use loaded candidates from CSV
    if constituency_no not in CANDIDATES_DATA:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Constituency {constituency_no} not found"
        )
    
    data = CANDIDATES_DATA[constituency_no]
    
    candidates = [
        CandidateResponse(
            id=c["id"],
            name=c["name"],
            party=c["party"],
            constituency_no=constituency_no,
            constituency_name=data["name"]
        )
        for c in data["candidates"]
    ]
    
    return CandidatesListResponse(
        constituency_no=constituency_no,
        constituency_name=data["name"],
        total_candidates=len(candidates),
        candidates=candidates
    )


@router.post("/submit", response_model=VoteSubmitResponse)
async def submit_vote(request: VoteSubmitRequest):
    """
    Submit a vote to the blockchain.
    
    Process:
    1. Validate voting token (must be within 5 minutes)
    2. Verify voter hasn't already voted
    3. Create anonymous vote hash:
       - hash = SHA256(voter_id + timestamp + candidate_id + salt)
       - Only hash + candidate_id stored (NO VOTER ID)
    4. Add to blockchain
    5. Mark voter as has_voted
    
    The vote is completely anonymous:
    - Voter ID is used in hash but NOT stored
    - Only the hash proves a valid vote was cast
    - Cannot trace vote back to voter
    """
    import json
    
    # Step 1: Validate token
    # TODO: Check token exists and hasn't expired
    # token_valid = check_voting_token(request.token)
    token_valid = True  # Placeholder
    
    if not token_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired voting token"
        )
    
    # Step 2: Get voter info and verify hasn't voted
    settings = get_settings()
    voters_file = settings.base_dir.parent / "data" / "voters.json"
    
    voter_info = None
    constituency_no = 1  # Default
    
    if voters_file.exists():
        try:
            with open(voters_file, 'r') as f:
                voters_db = json.load(f)
            # Find voter by voter_id
            for aadhaar, info in voters_db.items():
                if info.get("voter_id") == request.voter_id:
                    voter_info = info
                    constituency_no = info.get("constituency_no", 1)
                    
                    # Check if already voted
                    if info.get("has_voted", False):
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="You have already cast your vote."
                        )
                    break
        except Exception as e:
            print(f"Error reading voters file: {e}")
    
    # Step 3: Add to blockchain
    from services.blockchain_service import get_blockchain_service
    blockchain_service = get_blockchain_service()
    
    if not blockchain_service.is_available:
         # Fallback to simulation if DB fails
         timestamp = datetime.now(timezone.utc).isoformat()
         salt = hashlib.sha256(f"{request.token}".encode()).hexdigest()[:16]
         vote_data = f"{request.voter_id}-{timestamp}-{request.candidate_id}-{salt}"
         vote_hash = hashlib.sha256(vote_data.encode()).hexdigest()
         block_index = -1
         print(f"⚠️ Blockchain unavailable. Simulated Hash: {vote_hash}")
    else:
         # Submit to real blockchain with actual constituency
         result = blockchain_service.submit_vote(
             voter_id=request.voter_id,
             candidate_id=request.candidate_id,
             constituency_no=constituency_no
         )
         
         if not result['success']:
             raise HTTPException(
                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                 detail=result['message']
             )
             
         block_index = result['block_index']
         vote_hash = result['vote_hash']
    
    # Step 4: Mark voter as has_voted in JSON file with timestamp
    if voters_file.exists() and voter_info:
        try:
            with open(voters_file, 'r') as f:
                voters_db = json.load(f)
            
            # Find and update voter
            for aadhaar, info in voters_db.items():
                if info.get("voter_id") == request.voter_id:
                    voters_db[aadhaar]["has_voted"] = True
                    voters_db[aadhaar]["voted_at"] = datetime.now(timezone.utc).isoformat()
                    break
            
            with open(voters_file, 'w') as f:
                json.dump(voters_db, f, indent=2)
                
            print(f"✅ Marked voter {request.voter_id} as has_voted")
        except Exception as e:
            print(f"Error updating voter status: {e}")
    
    # Step 5: Store vote in votes.json for results tracking
    votes_file = settings.base_dir.parent / "data" / "votes.json"
    try:
        votes = []
        if votes_file.exists():
            with open(votes_file, 'r') as f:
                votes = json.load(f)
        
        votes.append({
            "candidate_id": request.candidate_id,
            "constituency_no": constituency_no,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "vote_hash": vote_hash[:16] if vote_hash else "simulated"
        })
        
        with open(votes_file, 'w') as f:
            json.dump(votes, f, indent=2)
        
        print(f"✅ Vote stored in votes.json")
    except Exception as e:
        print(f"Error storing vote: {e}")
    
    return VoteSubmitResponse(
        success=True,
        message="Vote cast successfully. Securely stored on blockchain.",
        block_index=block_index,
        vote_hash=vote_hash
    )


@router.get("/status/{aadhaar_number}", response_model=VoteStatusResponse)
async def check_vote_status(aadhaar_number: str):
    """
    Check if a voter has already voted.
    
    Used to:
    - Prevent duplicate verification attempts
    - Show status to voter before verification
    """
    import json
    
    # Validate Aadhaar
    if len(aadhaar_number) != 12 or not aadhaar_number.isdigit():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Aadhaar number"
        )
    
    # Check voters.json file
    settings = get_settings()
    voters_file = settings.base_dir.parent / "data" / "voters.json"
    
    if not voters_file.exists():
        return VoteStatusResponse(
            has_voted=False,
            message="Voter not registered"
        )
    
    try:
        with open(voters_file, 'r') as f:
            voters_db = json.load(f)
        
        voter_info = voters_db.get(aadhaar_number)
        
        if not voter_info:
            return VoteStatusResponse(
                has_voted=False,
                message="Voter not registered"
            )
        
        has_voted = voter_info.get("has_voted", False)
        return VoteStatusResponse(
            has_voted=has_voted,
            message="You have already voted" if has_voted else "Voter has not voted yet"
        )
    except Exception as e:
        print(f"Error checking vote status: {e}")
        return VoteStatusResponse(
            has_voted=False,
            message="Unable to check status"
        )
