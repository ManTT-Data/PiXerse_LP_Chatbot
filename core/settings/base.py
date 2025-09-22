from pydantic_settings import BaseSettings
from typing import Optional
import os
from pydantic import SecretStr


class Settings(BaseSettings):
    """Application settings"""
    
    # Database
    database_url: SecretStr = os.getenv("DATABASE_URL", "")
    
    # OpenAI
    openai_api_key: SecretStr = os.getenv("OPENAI_API_KEY", "")
    
    # Application
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Security
    secret_key: SecretStr = os.getenv("SECRET_KEY", "your_secret_key_here")

    # Logging
    log_level: str = "INFO"
    
    # CORS
    allowed_origins: str = "http://localhost:3000,http://localhost:8080,http://127.0.0.1:3000"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
