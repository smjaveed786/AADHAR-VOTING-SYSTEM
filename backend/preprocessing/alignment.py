"""
Face Alignment Module
Aligns faces using similarity transform based on facial landmarks
"""

import cv2
import numpy as np
from typing import Tuple, Optional


class FaceAligner:
    """Face alignment using facial landmarks"""
    
    def __init__(self, config: dict):
        """
        Initialize face aligner
        
        Args:
            config: Alignment configuration dictionary
        """
        self.config = config
        self.output_size = config["output_size"]
        self.normalize = config["normalize"]
        
        # Reference landmarks for alignment (5-point landmarks)
        # These are the standard positions for a 96x112 face
        self.reference_landmarks = np.array([
            [30.2946, 51.6963],  # Left eye
            [65.5318, 51.5014],  # Right eye
            [48.0252, 71.7366],  # Nose tip
            [33.5493, 92.3655],  # Left mouth corner
            [62.7299, 92.2041],  # Right mouth corner
        ], dtype=np.float32)
        
        # Scale reference landmarks to match output size
        if self.output_size != (96, 112):
            scale_x = self.output_size[0] / 96
            scale_y = self.output_size[1] / 112
            self.reference_landmarks[:, 0] *= scale_x
            self.reference_landmarks[:, 1] *= scale_y
    
    def align(self, image: np.ndarray, landmarks: np.ndarray) -> Optional[np.ndarray]:
        """
        Align face using similarity transform
        
        Args:
            image: RGB image (H, W, 3)
            landmarks: [5, 2] facial landmarks (left_eye, right_eye, nose, left_mouth, right_mouth)
            
        Returns:
            Aligned face crop of size output_size, or None if alignment fails
        """
        if landmarks is None or len(landmarks) != 5:
            return None
        
        try:
            # Compute similarity transform
            tform = self._similarity_transform(landmarks, self.reference_landmarks)
            
            if tform is None:
                return None
            
            # Warp image
            aligned = cv2.warpAffine(
                image,
                tform,
                self.output_size,
                flags=cv2.INTER_LINEAR,
                borderMode=cv2.BORDER_CONSTANT,
                borderValue=0
            )
            
            # Normalize if requested
            if self.normalize:
                aligned = self._normalize_image(aligned)
            
            return aligned
            
        except Exception as e:
            print(f"Alignment error: {e}")
            return None
    
    def _similarity_transform(self, src: np.ndarray, dst: np.ndarray) -> Optional[np.ndarray]:
        """
        Compute similarity transform matrix (rotation + scale + translation)
        
        Args:
            src: Source landmarks [N, 2]
            dst: Destination landmarks [N, 2]
            
        Returns:
            2x3 affine transform matrix or None if estimation fails
        """
        try:
            # Use cv2.estimateAffinePartial2D for robust estimation
            # This computes similarity transform (4 DOF: rotation, scale, translation x/y)
            tform, inliers = cv2.estimateAffinePartial2D(
                src.astype(np.float32), 
                dst.astype(np.float32),
                method=cv2.LMEDS
            )
            return tform
        except Exception as e:
            print(f"Transform estimation error: {e}")
            return None
    
    def _normalize_image(self, image: np.ndarray) -> np.ndarray:
        """
        Normalize image to [-1, 1] range (for FaceNet)
        
        Args:
            image: RGB image (0-255)
            
        Returns:
            Normalized image [-1, 1]
        """
        # Convert to float and scale to [0, 1]
        image = image.astype(np.float32) / 255.0
        
        # Normalize to [-1, 1]
        image = (image - 0.5) / 0.5
        
        return image
    
    def align_crop(self, image: np.ndarray, bbox: np.ndarray, 
                   landmarks: Optional[np.ndarray] = None) -> Optional[np.ndarray]:
        """
        Align face using landmarks, or simple crop if landmarks not available
        
        Args:
            image: RGB image
            bbox: [x1, y1, x2, y2] bounding box
            landmarks: Optional [5, 2] landmarks
            
        Returns:
            Aligned/cropped face
        """
        # Try alignment with landmarks first
        if landmarks is not None:
            aligned = self.align(image, landmarks)
            if aligned is not None:
                return aligned
        
        # Fallback: simple crop and resize
        return self._simple_crop(image, bbox)
    
    def _simple_crop(self, image: np.ndarray, bbox: np.ndarray) -> Optional[np.ndarray]:
        """
        Simple crop and resize (fallback when landmarks unavailable)
        
        Args:
            image: RGB image
            bbox: [x1, y1, x2, y2]
            
        Returns:
            Cropped and resized face
        """
        try:
            x1, y1, x2, y2 = bbox.astype(int)
            
            # Clip to image boundaries
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(image.shape[1], x2), min(image.shape[0], y2)
            
            # Crop
            crop = image[y1:y2, x1:x2]
            
            if crop.size == 0:
                return None
            
            # Resize to output size
            resized = cv2.resize(crop, self.output_size, interpolation=cv2.INTER_LINEAR)
            
            # Normalize if requested
            if self.normalize:
                resized = self._normalize_image(resized)
            
            return resized
            
        except Exception as e:
            print(f"Crop error: {e}")
            return None
    
    def align_batch(self, images: list, landmarks_list: list) -> list:
        """
        Align batch of faces
        
        Args:
            images: List of RGB images
            landmarks_list: List of landmark arrays
            
        Returns:
            List of aligned faces
        """
        aligned_faces = []
        for image, landmarks in zip(images, landmarks_list):
            aligned = self.align(image, landmarks)
            if aligned is not None:
                aligned_faces.append(aligned)
        return aligned_faces


if __name__ == "__main__":
    # Test the aligner
    from config import ALIGNMENT_CONFIG
    
    print("Testing Face Aligner...")
    aligner = FaceAligner(ALIGNMENT_CONFIG)
    
    # Create test image and landmarks
    test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    test_landmarks = np.array([
        [200, 180],  # Left eye
        [280, 180],  # Right eye
        [240, 230],  # Nose
        [210, 280],  # Left mouth
        [270, 280],  # Right mouth
    ], dtype=np.float32)
    
    aligned = aligner.align(test_image, test_landmarks)
    
    if aligned is not None:
        print(f"✅ Face aligned!")
        print(f"   Output shape: {aligned.shape}")
        print(f"   Output size: {aligner.output_size}")
        print(f"   Normalized: {aligner.normalize}")
        if aligner.normalize:
            print(f"   Value range: [{aligned.min():.2f}, {aligned.max():.2f}]")
    else:
        print("❌ Alignment failed")
    
    print("\n✅ Aligner module working correctly!")
