from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Database - Default to Aiven PostgreSQL
    database_url: str = ""
    
    # OpenAI
    openai_api_key: str = ""
    
    # Application
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Security
    secret_key: str = "your_secret_key_here"
    
    # Logging
    log_level: str = "INFO"
    
    # CORS
    allowed_origins: str = "http://localhost:3000,http://localhost:8080,http://127.0.0.1:3000"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
