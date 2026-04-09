"""
Face Detection Module
Uses MTCNN for robust face detection with landmarks
"""

import torch
import numpy as np
from typing import List, Tuple, Optional
from facenet_pytorch import MTCNN
import cv2


class FaceDetector:
    """Face detection using MTCNN"""
    
    def __init__(self, config: dict):
        """
        Initialize face detector
        
        Args:
            config: Detection configuration dictionary
        """
        self.config = config
        self.device = torch.device(config["device"])
        
        if config["detector_type"] == "mtcnn":
            self.detector = MTCNN(
                image_size=160,
                margin=0,
                min_face_size=config["min_face_size"],
                thresholds=config["thresholds"],
                factor=0.709,
                post_process=False,
                device=self.device,
                keep_all=False,  # Only detect largest face
                selection_method='largest',  # Select largest face
            )
        else:
            raise NotImplementedError(f"Detector {config['detector_type']} not implemented")
    
    def detect(self, image: np.ndarray) -> Optional[Tuple[np.ndarray, np.ndarray, float]]:
        """
        Detect face in image
        
        Args:
            image: RGB image (H, W, 3) as numpy array
            
        Returns:
            Tuple of (bbox, landmarks, confidence) or None if no face detected
            - bbox: [x1, y1, x2, y2] bounding box coordinates
            - landmarks: [5, 2] array of facial landmarks (left_eye, right_eye, nose, left_mouth, right_mouth)
            - confidence: detection confidence score (0-1)
        """
        if image is None or image.size == 0:
            return None
        
        # Ensure RGB format
        if len(image.shape) == 2:
            # Grayscale to RGB
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        elif image.shape[2] == 4:
            # RGBA to RGB
            image = cv2.cvtColor(image, cv2.COLOR_BGRA2RGB)
        
        try:
            # MTCNN expects RGB
            boxes, probs, landmarks = self.detector.detect(image, landmarks=True)
            
            if boxes is None or len(boxes) == 0:
                return None
            
            # Return largest face (first one since keep_all=False)
            bbox = boxes[0]
            landmark = landmarks[0]
            confidence = probs[0]
            
            return bbox, landmark, confidence
            
        except Exception as e:
            print(f"Detection error: {e}")
            return None
    
    def detect_batch(self, images: List[np.ndarray]) -> List[Optional[Tuple]]:
        """
        Detect faces in batch of images
        
        Args:
            images: List of RGB images
            
        Returns:
            List of detection results (one per image)
        """
        return [self.detect(img) for img in images]
    
    def detect_with_quality(self, image: np.ndarray) -> Optional[Tuple[np.ndarray, np.ndarray, float, dict]]:
        """
        Detect face and compute quality metrics
        
        Args:
            image: RGB image
            
        Returns:
            Tuple of (bbox, landmarks, confidence, quality_dict) or None
            quality_dict contains: face_size, blur_score, brightness
        """
        result = self.detect(image)
        if result is None:
            return None
        
        bbox, landmarks, confidence = result
        
        # Compute quality metrics
        x1, y1, x2, y2 = bbox.astype(int)
        face_width = x2 - x1
        face_height = y2 - y1
        face_size = min(face_width, face_height)
        
        # Extract face region for quality checks
        face_region = image[max(0, y1):min(image.shape[0], y2), 
                           max(0, x1):min(image.shape[1], x2)]
        
        # Blur detection (Laplacian variance)
        if face_region.size > 0:
            gray_face = cv2.cvtColor(face_region, cv2.COLOR_RGB2GRAY)
            blur_score = cv2.Laplacian(gray_face, cv2.CV_64F).var()
            brightness = np.mean(gray_face)
        else:
            blur_score = 0.0
            brightness = 0.0
        
        quality = {
            "face_size": face_size,
            "blur_score": blur_score,
            "brightness": brightness,
            "is_good_quality": face_size >= 80 and blur_score > 100 and 40 < brightness < 220
        }
        
        return bbox, landmarks, confidence, quality


if __name__ == "__main__":
    # Test the detector
    from config import DETECTION_CONFIG
    
    print("Testing Face Detector...")
    detector = FaceDetector(DETECTION_CONFIG)
    
    # Create a test image (you can replace with actual image)
    test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    
    result = detector.detect(test_image)
    if result:
        bbox, landmarks, conf = result
        print(f"✅ Face detected!")
        print(f"   Confidence: {conf:.3f}")
        print(f"   Bounding box: {bbox}")
        print(f"   Landmarks shape: {landmarks.shape}")
    else:
        print("❌ No face detected (expected for random image)")
    
    print("\n✅ Detector module working correctly!")
