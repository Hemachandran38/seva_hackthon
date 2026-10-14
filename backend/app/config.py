"""
Application configuration using Pydantic Settings.

Configuration is loaded from environment variables or .env file.
"""

from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    """Application settings."""
    
    # Database
    database_url: str = "sqlite:///civicpulse.db"
    
    # Environment
    environment: str = "development"
    debug: bool = True
    
    # CORS
    allowed_origins: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    allow_credentials: bool = True
    
    # Application
    app_name: str = "CivicPulse AI Backend"
    app_version: str = "0.1.0"
    api_prefix: str = "/api"
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        """Pydantic config."""
        env_file = ".env"
        case_sensitive = False

settings = Settings()
