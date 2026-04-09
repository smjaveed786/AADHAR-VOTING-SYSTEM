"""
Configuration file for Voter Verification System
Contains all hyperparameters and settings for each component
"""

import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent
MODELS_DIR = BASE_DIR / "models" / "pretrained"
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
CLIPS_DIR = LOGS_DIR / "clips"

# Create directories if they don't exist
for dir_path in [MODELS_DIR, DATA_DIR, LOGS_DIR, CLIPS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# ============================================================================
# DETECTION & ALIGNMENT CONFIGURATION
# ============================================================================

DETECTION_CONFIG = {
    "detector_type": "mtcnn",  # Face detector to use
    "min_face_size": 40,       # Minimum face size in pixels
    "thresholds": [0.6, 0.7, 0.7],  # MTCNN detection thresholds [P-Net, R-Net, O-Net]
    "device": "cuda" if os.environ.get("CUDA_VISIBLE_DEVICES") else "cpu",
}

ALIGNMENT_CONFIG = {
    "output_size": (160, 160),  # Output size for aligned faces (FaceNet expects 160x160)
    "normalize": True,          # Normalize to [-1, 1] range
}

# ============================================================================
# TIER A: PASSIVE PAD CONFIGURATION
# ============================================================================

PAD_CONFIG = {
    "model_name": "mobilenetv2_100",  # Backbone: mobilenetv2_100 or efficientnet_lite0
    "pretrained": True,               # Use ImageNet pretrained weights
    "num_classes": 2,                 # Binary: real vs spoof
    "input_size": (224, 224),         # Input image size
    "num_frames": 3,                  # Number of frames to average for prediction
    "threshold": 0.7,                 # Decision threshold (tune on Day 10)
    "device": "cuda" if os.environ.get("CUDA_VISIBLE_DEVICES") else "cpu",
}

# ============================================================================
# TIER B: ACTIVE CHALLENGE CONFIGURATION
# ============================================================================

ACTIVE_CHALLENGE_CONFIG = {
    "actions": ["blink", "look_left", "look_right", "look_up"],  # Available actions
    "sequence_length": (1, 3),        # Random sequence length (min, max)
    "timeout": 3.0,                   # Timeout per action in seconds
    "blink_ear_threshold": 0.21,      # Eye Aspect Ratio threshold for blink
    "blink_consecutive_frames": 2,    # Consecutive frames with closed eyes
    "head_yaw_threshold": 15,         # Head turn angle threshold (degrees)
    "head_pitch_threshold": 15,       # Head pitch angle threshold (degrees)
    "use_face_flashing": False,       # Enable face flashing (optional)
    "flash_pattern_length": 5,        # Flash pattern length in frames
}

# ============================================================================
# TIER C: ADVANCED LIVENESS (rPPG) - OPTIONAL
# ============================================================================

RPPG_CONFIG = {
    "enabled": False,                 # Enable Tier C (set True for high-security scenarios)
    "method": "POS",                  # rPPG method: "POS" or "ICA"
    "fps": 30,                        # Video frame rate
    "window_size": 90,                # Window size in frames (3 seconds at 30fps)
    "hr_range": (50, 120),            # Valid heart rate range (BPM)
}

# ============================================================================
# FACE RECOGNITION CONFIGURATION
# ============================================================================

RECOGNITION_CONFIG = {
    "model_type": "facenet",          # Recognition model: "facenet" or "arcface"
    "pretrained_dataset": "vggface2", # Pretrained dataset: "vggface2" or "casia-webface"
    "embedding_size": 512,            # Embedding dimension
    "threshold": 0.6,                 # Cosine similarity threshold (tune on Day 10)
    "device": "cuda" if os.environ.get("CUDA_VISIBLE_DEVICES") else "cpu",
}

# ============================================================================
# PIPELINE CONFIGURATION
# ============================================================================

PIPELINE_CONFIG = {
    "capture_duration": 3.0,          # Video capture duration in seconds
    "fps": 30,                        # Frame rate
    "enable_tier_c": False,           # Enable Tier C (rPPG)
    "max_retries": 1,                 # Number of retries for failed challenges
    "latency_target": 3.0,            # Target latency in seconds
}

# ============================================================================
# LOGGING & PRIVACY CONFIGURATION
# ============================================================================

LOGGING_CONFIG = {
    "encrypt_clips": True,                      # Encrypt stored video clips
    "encryption_key_env": "VOTER_VERIFY_KEY",   # Environment variable for encryption key
    "retention_days": 30,                       # Log retention period
    "log_level": "INFO",                        # Logging level
    "store_raw_clips": True,                    # Store video clips (set False for privacy)
}

# ============================================================================
# EVALUATION METRICS TARGETS
# ============================================================================

METRICS_TARGETS = {
    "pad": {
        "apcer": 0.01,  # Attack Presentation Classification Error Rate (target <1%)
        "bpcer": 0.05,  # Bona Fide Presentation Classification Error Rate (target <5%)
    },
    "recognition": {
        "far": 1e-4,    # False Accept Rate (target <0.01%)
        "tar": 0.99,    # True Accept Rate at target FAR (target >99%)
    },
}

# ============================================================================
# DATASET PATHS
# ============================================================================

DATASET_PATHS = {
    "pad_train": DATA_DIR / "pad" / "train",
    "pad_val": DATA_DIR / "pad" / "val",
    "pad_test": DATA_DIR / "pad" / "test",
    "recognition_train": DATA_DIR / "recognition" / "train",
    "recognition_val": DATA_DIR / "recognition" / "val",
    "user_database": DATA_DIR / "user_database.json",  # Stored user embeddings
}

# ============================================================================
# TRAINING CONFIGURATION
# ============================================================================

TRAINING_CONFIG = {
    "pad": {
        "batch_size": 32,
        "learning_rate": 2e-4,
        "epochs": 10,
        "freeze_backbone": True,      # Freeze backbone, only train classifier
        "optimizer": "adam",
        "scheduler": "cosine",
        "weight_decay": 1e-4,
        "early_stopping_patience": 3,
    },
}

# ============================================================================
# PRINT CONFIGURATION SUMMARY
# ============================================================================

def print_config_summary():
    """Print configuration summary"""
    print("=" * 70)
    print("VOTER VERIFICATION SYSTEM - CONFIGURATION")
    print("=" * 70)
    print(f"Base Directory: {BASE_DIR}")
    print(f"Device: {DETECTION_CONFIG['device']}")
    print(f"Face Detector: {DETECTION_CONFIG['detector_type']}")
    print(f"PAD Model: {PAD_CONFIG['model_name']}")
    print(f"Recognition Model: {RECOGNITION_CONFIG['model_type']}")
    print(f"Tier C (rPPG): {'Enabled' if RPPG_CONFIG['enabled'] else 'Disabled'}")
    print(f"Target Latency: {PIPELINE_CONFIG['latency_target']}s")
    print("=" * 70)

if __name__ == "__main__":
    print_config_summary()
