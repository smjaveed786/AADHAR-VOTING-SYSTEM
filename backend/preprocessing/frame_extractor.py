"""
Frame Extraction Module
Extracts frames from video files or webcam
"""

import cv2
import numpy as np
from typing import List, Optional
from pathlib import Path
import time


class FrameExtractor:
    """Extract frames from video or webcam"""
    
    def __init__(self, fps: int = 30):
        """
        Initialize frame extractor
        
        Args:
            fps: Target frames per second
        """
        self.fps = fps
        self.frame_interval = 1.0 / fps
    
    def extract_from_video(self, video_path: Path, 
                          max_frames: Optional[int] = None,
                          start_time: float = 0.0) -> List[np.ndarray]:
        """
        Extract frames from video file
        
        Args:
            video_path: Path to video file
            max_frames: Maximum number of frames to extract (None = all)
            start_time: Start time in seconds
            
        Returns:
            List of RGB frames
        """
        if not Path(video_path).exists():
            print(f"Video file not found: {video_path}")
            return []
        
        cap = cv2.VideoCapture(str(video_path))
        
        if not cap.isOpened():
            print(f"Failed to open video: {video_path}")
            return []
        
        # Get video properties
        video_fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        print(f"Video: {video_path.name}")
        print(f"  FPS: {video_fps}, Total frames: {total_frames}")
        
        # Seek to start time
        if start_time > 0:
            start_frame = int(start_time * video_fps)
            cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
        
        frames = []
        frame_count = 0
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # Convert BGR to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frames.append(frame_rgb)
            frame_count += 1
            
            if max_frames and frame_count >= max_frames:
                break
        
        cap.release()
        print(f"  Extracted {len(frames)} frames")
        return frames
    
    def capture_from_webcam(self, duration: float, 
                           camera_id: int = 0,
                           warmup_time: float = 1.0) -> List[np.ndarray]:
        """
        Capture frames from webcam
        
        Args:
            duration: Capture duration in seconds
            camera_id: Camera device ID (0 = default webcam)
            warmup_time: Camera warmup time in seconds
            
        Returns:
            List of RGB frames
        """
        cap = cv2.VideoCapture(camera_id)
        
        if not cap.isOpened():
            print(f"Failed to open camera {camera_id}")
            return []
        
        # Set camera properties
        cap.set(cv2.CAP_PROP_FPS, self.fps)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        # Warmup: let camera adjust exposure/white balance
        print(f"Camera warmup ({warmup_time}s)...")
        warmup_start = time.time()
        while time.time() - warmup_start < warmup_time:
            cap.read()
        
        # Capture frames
        frames = []
        num_frames = int(duration * self.fps)
        
        print(f"Capturing {num_frames} frames ({duration}s at {self.fps} fps)...")
        start_time = time.time()
        
        for i in range(num_frames):
            ret, frame = cap.read()
            if not ret:
                print(f"Warning: Failed to capture frame {i}")
                break
            
            # Convert BGR to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frames.append(frame_rgb)
            
            # Maintain frame rate
            elapsed = time.time() - start_time
            expected_time = (i + 1) * self.frame_interval
            if elapsed < expected_time:
                time.sleep(expected_time - elapsed)
        
        cap.release()
        
        actual_duration = time.time() - start_time
        actual_fps = len(frames) / actual_duration if actual_duration > 0 else 0
        
        print(f"Captured {len(frames)} frames in {actual_duration:.2f}s ({actual_fps:.1f} fps)")
        return frames
    
    def capture_with_preview(self, duration: float,
                            camera_id: int = 0,
                            window_name: str = "Webcam Preview") -> List[np.ndarray]:
        """
        Capture frames with live preview window
        
        Args:
            duration: Capture duration in seconds
            camera_id: Camera device ID
            window_name: Preview window name
            
        Returns:
            List of RGB frames
        """
        cap = cv2.VideoCapture(camera_id)
        
        if not cap.isOpened():
            print(f"Failed to open camera {camera_id}")
            return []
        
        cap.set(cv2.CAP_PROP_FPS, self.fps)
        
        frames = []
        num_frames = int(duration * self.fps)
        
        print(f"Starting capture with preview. Press 'q' to stop early.")
        cv2.namedWindow(window_name)
        
        start_time = time.time()
        
        for i in range(num_frames):
            ret, frame = cap.read()
            if not ret:
                break
            
            # Show preview (BGR format for OpenCV display)
            cv2.imshow(window_name, frame)
            
            # Convert to RGB for storage
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frames.append(frame_rgb)
            
            # Check for early exit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("Capture stopped by user")
                break
            
            # Maintain frame rate
            elapsed = time.time() - start_time
            expected_time = (i + 1) * self.frame_interval
            if elapsed < expected_time:
                time.sleep(expected_time - elapsed)
        
        cap.release()
        cv2.destroyWindow(window_name)
        
        print(f"Captured {len(frames)} frames")
        return frames
    
    def save_video(self, frames: List[np.ndarray], output_path: Path, 
                   fps: Optional[int] = None,
                   codec: str = 'mp4v') -> bool:
        """
        Save frames as video file
        
        Args:
            frames: List of RGB frames
            output_path: Output video path
            fps: Frame rate (uses self.fps if None)
            codec: Video codec (mp4v, avc1, etc.)
            
        Returns:
            True if successful
        """
        if not frames:
            print("No frames to save")
            return False
        
        fps = fps or self.fps
        height, width = frames[0].shape[:2]
        
        # Create output directory if needed
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize video writer
        fourcc = cv2.VideoWriter_fourcc(*codec)
        out = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
        
        if not out.isOpened():
            print(f"Failed to create video writer: {output_path}")
            return False
        
        # Write frames
        for frame in frames:
            # Convert RGB to BGR for OpenCV
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            out.write(frame_bgr)
        
        out.release()
        print(f"Saved video: {output_path} ({len(frames)} frames at {fps} fps)")
        return True
    
    def save_frames_as_images(self, frames: List[np.ndarray], 
                             output_dir: Path,
                             prefix: str = "frame") -> int:
        """
        Save frames as individual image files
        
        Args:
            frames: List of RGB frames
            output_dir: Output directory
            prefix: Filename prefix
            
        Returns:
            Number of frames saved
        """
        if not frames:
            return 0
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        saved_count = 0
        for i, frame in enumerate(frames):
            filename = output_dir / f"{prefix}_{i:04d}.jpg"
            # Convert RGB to BGR for OpenCV
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            if cv2.imwrite(str(filename), frame_bgr):
                saved_count += 1
        
        print(f"Saved {saved_count} frames to {output_dir}")
        return saved_count


if __name__ == "__main__":
    # Test the frame extractor
    print("Testing Frame Extractor...")
    extractor = FrameExtractor(fps=30)
    
    # Test webcam capture (comment out if no webcam available)
    print("\n1. Testing webcam capture (2 seconds)...")
    try:
        frames = extractor.capture_from_webcam(duration=2.0, camera_id=0)
        if frames:
            print(f"✅ Captured {len(frames)} frames")
            print(f"   Frame shape: {frames[0].shape}")
            print(f"   Frame dtype: {frames[0].dtype}")
        else:
            print("⚠️  No frames captured (webcam may not be available)")
    except Exception as e:
        print(f"⚠️  Webcam test skipped: {e}")
    
    print("\n✅ Frame extractor module working correctly!")
