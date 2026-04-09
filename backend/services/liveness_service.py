"""
Liveness Detection Service

This service provides:
- Video frame processing for spoof detection
- Real/spoof classification using trained model
- Confidence scoring

Uses the production liveness model: models/liveness_detector_production.pth
"""

import os
from pathlib import Path
from typing import Optional, Tuple, List, Dict
import numpy as np

from settings import get_settings


class LivenessDetector:
    """
    Liveness Detection Model using MobileNetV2 backbone.
    Must match the architecture used during training.
    """
    
    def __init__(self, pretrained=False, dropout=0.5):
        import torch.nn as nn
        from torchvision import models
        
        # Using nn.Module methods
        self.backbone = models.mobilenet_v2(weights=None)
        
        # Get feature dimension from the last layer
        self.feature_dim = self.backbone.classifier[1].in_features
        
        # Replace classifier with custom head (same as training)
        self.backbone.classifier = nn.Sequential(
            nn.Dropout(dropout),
            nn.Linear(self.feature_dim, 256),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout / 2),
            nn.Linear(256, 2)  # [spoof, real]
        )
    
    def __call__(self, x):
        return self.backbone(x)
    
    def to(self, device):
        self.backbone = self.backbone.to(device)
        return self
    
    def eval(self):
        self.backbone.eval()
        return self
    
    def load_state_dict(self, state_dict, strict=True):
        return self.backbone.load_state_dict(state_dict, strict=strict)
    
    def state_dict(self):
        return self.backbone.state_dict()


class LivenessService:
    """
    Liveness detection service using trained PyTorch model.
    
    The model classifies faces as:
    - Real (live person)
    - Spoof (photo, video, mask)
    
    IMPORTANT: Uses face detection + crop before liveness classification.
    The model was trained on cropped face images, not full frames.
    """
    
    _instance = None
    _model = None
    _transform = None
    _device = None
    _face_net = None  # OpenCV DNN face detector
    
    def __new__(cls):
        """Singleton pattern to avoid loading model multiple times."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize liveness detection model."""
        if self._model is not None:
            return
        
        try:
            import torch
            import torch.nn as nn
            from torchvision import transforms, models
            
            settings = get_settings()
            # Use the model path from settings, or default to production model
            model_name = Path(settings.liveness_model_path).name
            model_path = settings.models_dir / model_name
            
            if not model_path.exists():
                print(f"⚠️ Liveness model not found at: {model_path}")
                print("Liveness detection will not be available.")
                return
            
            print(f"Loading liveness model from: {model_path}")
            
            # Set device (use MPS for Mac, CUDA for GPU, else CPU)
            if torch.backends.mps.is_available():
                self._device = torch.device('mps')
            elif torch.cuda.is_available():
                self._device = torch.device('cuda')
            else:
                self._device = torch.device('cpu')
            
            print(f"Using device: {self._device}")
            
            # Create model architecture (MUST match training architecture)
            self._model = LivenessDetector(pretrained=False)
            
            # Load trained weights
            checkpoint = torch.load(model_path, map_location=self._device, weights_only=False)
            
            # Handle different checkpoint formats
            state_dict = checkpoint
            if 'model_state_dict' in checkpoint:
                state_dict = checkpoint['model_state_dict']
            
            # Remove 'backbone.' prefix from keys (model was saved with this prefix)
            new_state_dict = {}
            for k, v in state_dict.items():
                if k.startswith('backbone.'):
                    new_state_dict[k[9:]] = v  # Remove 'backbone.' prefix
                else:
                    new_state_dict[k] = v
            
            # Load state dict into backbone
            self._model.backbone.load_state_dict(new_state_dict, strict=True)
            
            self._model.to(self._device)
            self._model.eval()
            
            # Define preprocessing (same as training)
            self._transform = transforms.Compose([
                transforms.ToPILImage(),
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406],
                    std=[0.229, 0.224, 0.225]
                )
            ])
            
            print("✅ Liveness model loaded!")
            
            # Load face detector (OpenCV DNN)
            self._load_face_detector()
            
        except Exception as e:
            print(f"⚠️ Failed to load liveness model: {e}")
            import traceback
            traceback.print_exc()
            print("Liveness detection will not be available.")
            self._model = None
    
    def _load_face_detector(self):
        """Load OpenCV DNN face detector."""
        import cv2
        import urllib.request
        
        settings = get_settings()
        face_detector_dir = settings.models_dir / 'face_detector'
        face_detector_dir.mkdir(exist_ok=True)
        
        prototxt_path = face_detector_dir / 'deploy.prototxt'
        caffemodel_path = face_detector_dir / 'res10_300x300_ssd_iter_140000.caffemodel'
        
        prototxt_url = "https://raw.githubusercontent.com/opencv/opencv/master/samples/dnn/face_detector/deploy.prototxt"
        caffemodel_url = "https://raw.githubusercontent.com/opencv/opencv_3rdparty/dnn_samples_face_detector_20170830/res10_300x300_ssd_iter_140000.caffemodel"
        
        try:
            if not prototxt_path.exists():
                print("Downloading face detector prototxt...")
                urllib.request.urlretrieve(prototxt_url, str(prototxt_path))
            
            if not caffemodel_path.exists():
                print("Downloading face detector model (10MB)...")
                urllib.request.urlretrieve(caffemodel_url, str(caffemodel_path))
            
            self._face_net = cv2.dnn.readNetFromCaffe(
                str(prototxt_path),
                str(caffemodel_path)
            )
            print("✅ Face detector loaded!")
            
        except Exception as e:
            print(f"⚠️ Failed to load face detector: {e}")
            self._face_net = None
    
    def _detect_face(self, frame: np.ndarray, confidence_threshold: float = 0.5) -> Tuple[Optional[Tuple[int, int, int, int]], float]:
        """Detect face in frame using OpenCV DNN."""
        if self._face_net is None:
            return None, 0.0
        
        h, w = frame.shape[:2]
        import cv2
        blob = cv2.dnn.blobFromImage(frame, 1.0, (300, 300), (104.0, 177.0, 123.0))
        self._face_net.setInput(blob)
        detections = self._face_net.forward()
        
        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > confidence_threshold:
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                x1, y1, x2, y2 = box.astype(int)
                return (x1, y1, x2, y2), confidence
        
        return None, 0.0
    
    def _crop_face(self, frame: np.ndarray, face_box: Tuple[int, int, int, int], padding: float = 0.2) -> np.ndarray:
        """Crop face region with padding."""
        x1, y1, x2, y2 = face_box
        h, w = frame.shape[:2]
        
        # Add padding
        pad_x = int((x2 - x1) * padding)
        pad_y = int((y2 - y1) * padding)
        x1 = max(0, x1 - pad_x)
        y1 = max(0, y1 - pad_y)
        x2 = min(w, x2 + pad_x)
        y2 = min(h, y2 + pad_y)
        
        return frame[y1:y2, x1:x2]
    
    @property
    def is_available(self) -> bool:
        """Check if liveness detection is available."""
        return self._model is not None
    
    def predict_frame(self, frame: np.ndarray) -> Tuple[str, float]:
        """
        Predict liveness for a single frame.
        
        IMPORTANT: Detects face first, crops it, then runs liveness on cropped face.
        This matches the training pipeline where the model was trained on cropped faces.
        
        Args:
            frame: BGR image (OpenCV format)
            
        Returns:
            verdict: "LIVE" or "SPOOF"
            confidence: float 0-1
        """
        if not self.is_available:
            return "UNKNOWN", 0.0
        
        import torch
        import cv2
        
        try:
            # Step 1: Detect face
            face_box, face_conf = self._detect_face(frame)
            
            if face_box is None:
                print("   No face detected in frame")
                return "UNKNOWN", 0.0
            
            # Step 2: Crop face with padding
            face_crop = self._crop_face(frame, face_box)
            
            if face_crop.size == 0:
                print("   Face crop is empty")
                return "UNKNOWN", 0.0
            
            # Step 3: Convert BGR to RGB
            face_rgb = cv2.cvtColor(face_crop, cv2.COLOR_BGR2RGB)
            
            # Step 4: Preprocess cropped face
            input_tensor = self._transform(face_rgb).unsqueeze(0).to(self._device)
            
            # Step 5: Predict on cropped face
            with torch.no_grad():
                outputs = self._model(input_tensor)
                probabilities = torch.softmax(outputs, dim=1)
                
                # Class 0 = Spoof, Class 1 = Real (as per training notebook)
                spoof_prob = probabilities[0, 0].item()
                real_prob = probabilities[0, 1].item()
                
                # Debug logging
                print(f"   Face crop prediction: spoof={spoof_prob:.4f}, real={real_prob:.4f}")
            
            if real_prob > spoof_prob:
                return "LIVE", real_prob
            else:
                return "SPOOF", spoof_prob
            
        except Exception as e:
            print(f"Error in liveness prediction: {e}")
            import traceback
            traceback.print_exc()
            return "UNKNOWN", 0.0
    
    def predict_frames(self, frames: List[np.ndarray]) -> Dict:
        """
        Predict liveness from multiple frames (video).
        
        Uses majority voting and average confidence.
        
        Args:
            frames: List of BGR images
            
        Returns:
            dict with verdict, confidence, and stats
        """
        if not self.is_available:
            return {
                "verdict": "UNKNOWN",
                "confidence": 0.0,
                "message": "Liveness model not available"
            }
        
        if len(frames) == 0:
            return {
                "verdict": "UNKNOWN",
                "confidence": 0.0,
                "message": "No frames provided"
            }
        
        live_count = 0
        spoof_count = 0
        confidences = []
        
        for frame in frames:
            verdict, confidence = self.predict_frame(frame)
            
            if verdict == "LIVE":
                live_count += 1
                confidences.append(confidence)
            elif verdict == "SPOOF":
                spoof_count += 1
                confidences.append(confidence)
        
        total = live_count + spoof_count
        
        if total == 0:
            return {
                "verdict": "UNKNOWN",
                "confidence": 0.0,
                "message": "Could not process any frames"
            }
        
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        # Majority voting
        if live_count > spoof_count:
            return {
                "verdict": "LIVE",
                "confidence": avg_confidence,
                "live_count": live_count,
                "spoof_count": spoof_count,
                "message": f"Detected live person ({live_count}/{total} frames)"
            }
        else:
            return {
                "verdict": "SPOOF",
                "confidence": avg_confidence,
                "live_count": live_count,
                "spoof_count": spoof_count,
                "message": f"Potential spoof detected ({spoof_count}/{total} frames)"
            }
    
    def predict_from_base64_frames(self, base64_frames: List[str]) -> Dict:
        """
        Predict liveness from base64 encoded frames.
        
        Args:
            base64_frames: List of base64 encoded images
            
        Returns:
            dict with verdict, confidence, and stats
        """
        import base64
        import cv2
        
        frames = []
        
        for b64_str in base64_frames:
            try:
                # Remove data URI prefix if present
                if ',' in b64_str:
                    b64_str = b64_str.split(',')[1]
                
                image_bytes = base64.b64decode(b64_str)
                nparr = np.frombuffer(image_bytes, np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                if frame is not None:
                    frames.append(frame)
                    
            except Exception as e:
                print(f"Error decoding frame: {e}")
                continue
        
        return self.predict_frames(frames)


# Singleton instance
liveness_service = LivenessService()
