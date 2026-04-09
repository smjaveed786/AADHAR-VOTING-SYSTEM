"""
Face Recognition Service using InsightFace

This service provides:
- Face detection
- Face embedding extraction (512-dim vectors)
- Face comparison using cosine similarity
- Voter matching from database

Based on the implementation in notebooks/face_recognition.ipynb
"""

import os
from pathlib import Path
from typing import Optional, Tuple, List, Dict
import numpy as np
import cv2

from settings import get_settings


class FaceService:
    """
    Face recognition service using InsightFace.
    
    Uses the buffalo_l model for:
    - Detection: RetinaFace
    - Recognition: ArcFace (512-dim embeddings)
    """
    
    _instance = None
    _app = None
    
    def __new__(cls):
        """Singleton pattern to avoid loading model multiple times."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize InsightFace model."""
        if self._app is not None:
            return
        
        try:
            from insightface.app import FaceAnalysis
            
            print("Loading InsightFace model...")
            self._app = FaceAnalysis(
                name='buffalo_l',  # Best accuracy model
                providers=['CPUExecutionProvider']  # Use CPU
            )
            self._app.prepare(ctx_id=-1, det_size=(640, 640))
            print("✅ InsightFace model loaded!")
            
        except Exception as e:
            print(f"⚠️ Failed to load InsightFace: {e}")
            print("Face recognition will not be available.")
            self._app = None
    
    @property
    def is_available(self) -> bool:
        """Check if face recognition is available."""
        return self._app is not None
    
    def generate_embedding(self, image: np.ndarray) -> Optional[np.ndarray]:
        """
        Extract face embedding from an image.
        
        Args:
            image: BGR image (OpenCV format) or RGB numpy array
            
        Returns:
            embedding: Normalized 512-dim numpy array, or None if no face detected
        """
        if not self.is_available:
            return None
        
        try:
            # Detect faces
            faces = self._app.get(image)
            
            if len(faces) == 0:
                return None
            
            # Get the largest face (in case multiple faces detected)
            face = max(
                faces, 
                key=lambda x: (x.bbox[2] - x.bbox[0]) * (x.bbox[3] - x.bbox[1])
            )
            
            # Extract embedding (512-dim vector)
            embedding = face.embedding
            
            # Normalize embedding
            embedding = embedding / np.linalg.norm(embedding)
            
            return embedding
            
        except Exception as e:
            print(f"Error extracting embedding: {e}")
            return None
    
    def generate_embedding_from_bytes(self, image_bytes: bytes) -> Optional[np.ndarray]:
        """
        Extract face embedding from image bytes (e.g., from uploaded file).
        
        Args:
            image_bytes: Raw image bytes
            
        Returns:
            embedding: Normalized 512-dim numpy array, or None if no face detected
        """
        try:
            # Decode image
            nparr = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                return None
            
            return self.generate_embedding(image)
            
        except Exception as e:
            print(f"Error decoding image: {e}")
            return None
    
    def generate_embedding_from_base64(self, base64_str: str) -> Optional[np.ndarray]:
        """
        Extract face embedding from base64 encoded image.
        
        Args:
            base64_str: Base64 encoded image string
            
        Returns:
            embedding: Normalized 512-dim numpy array, or None if no face detected
        """
        import base64
        
        try:
            # Remove data URI prefix if present
            if ',' in base64_str:
                base64_str = base64_str.split(',')[1]
            
            image_bytes = base64.b64decode(base64_str)
            return self.generate_embedding_from_bytes(image_bytes)
            
        except Exception as e:
            print(f"Error decoding base64: {e}")
            return None
    
    def compare_embeddings(
        self, 
        embedding1: np.ndarray, 
        embedding2: np.ndarray,
        threshold: float = 0.5
    ) -> Tuple[float, bool]:
        """
        Compare two face embeddings using cosine similarity.
        
        Args:
            embedding1: First face embedding (512-dim)
            embedding2: Second face embedding (512-dim)
            threshold: Similarity threshold (default 0.5)
            
        Returns:
            similarity: float between -1 and 1 (higher = more similar)
            is_match: bool based on threshold
        """
        # Cosine similarity (embeddings are already normalized)
        similarity = float(np.dot(embedding1, embedding2))
        is_match = similarity > threshold
        
        return similarity, is_match
    
    def generate_average_embedding(self, images: List[np.ndarray]) -> Optional[np.ndarray]:
        """
        Generate averaged embedding from multiple images.
        
        Useful for registration where multiple angles are captured.
        
        Args:
            images: List of BGR images
            
        Returns:
            embedding: Averaged and normalized 512-dim embedding
        """
        embeddings = []
        
        for image in images:
            embedding = self.generate_embedding(image)
            if embedding is not None:
                embeddings.append(embedding)
        
        if len(embeddings) == 0:
            return None
        
        # Average embeddings
        avg_embedding = np.mean(embeddings, axis=0)
        
        # Normalize
        avg_embedding = avg_embedding / np.linalg.norm(avg_embedding)
        
        return avg_embedding
    
    def detect_face(self, image: np.ndarray) -> Optional[Dict]:
        """
        Detect face and return bounding box info.
        
        Args:
            image: BGR image
            
        Returns:
            dict with bbox, score, or None if no face detected
        """
        if not self.is_available:
            return None
        
        try:
            faces = self._app.get(image)
            
            if len(faces) == 0:
                return None
            
            # Get largest face
            face = max(
                faces, 
                key=lambda x: (x.bbox[2] - x.bbox[0]) * (x.bbox[3] - x.bbox[1])
            )
            
            return {
                'bbox': face.bbox.astype(int).tolist(),
                'score': float(face.det_score),
                'landmarks': face.landmark_2d_106.tolist() if hasattr(face, 'landmark_2d_106') else None
            }
            
        except Exception as e:
            print(f"Error detecting face: {e}")
            return None


# Singleton instance
face_service = FaceService()
