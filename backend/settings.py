"""
Settings configuration using Pydantic Settings
Loads environment variables from .env file
"""

from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent / ".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    # Admin Authentication
    admin_username: str = "admin"
    admin_password: str = "admin123"
    
    # JWT Configuration
    jwt_secret_key: str = "voting-system-secret-key-dev-only-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60
    
    # Database
    database_url: str = "postgresql://postgres:password@localhost:5432/voting_system"
    
    # Models - using enhanced model with face detection + replay frame training
    liveness_model_path: str = "../models/liveness_detector_production.pth"
    
    # CORS - include all common frontend ports
    cors_origins: str = "http://localhost:5173,http://localhost:3000,http://localhost:5174,http://localhost:5175,http://127.0.0.1:5173,http://127.0.0.1:3000,http://localhost:5001"
    
    # Face Recognition
    face_similarity_threshold: float = 0.5
    registered_faces_dir: str = "../data/registered_faces"
    
    # Twilio OTP Configuration
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_phone_number: str = ""
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins string into list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    @property
    def base_dir(self) -> Path:
        """Get the base directory of the backend."""
        return Path(__file__).parent
    
    @property
    def models_dir(self) -> Path:
        """Get the models directory."""
        return self.base_dir.parent / "models"
    
    @property
    def data_dir(self) -> Path:
        """Get the data directory."""
        return self.base_dir.parent / "data"


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Uses lru_cache to avoid reading .env file on every request.
    """
    return Settings()
