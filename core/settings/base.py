from enum import Enum
from pathlib import Path
from tempfile import gettempdir
from typing import ClassVar, List, Optional

from pydantic import EmailStr, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

env_path = Path(__file__).parent.parent / "config" / ".env"

class Settings(BaseSettings):
    """Application settings"""
    
    database_url: SecretStr = SecretStr("")
    
    # OpenAI
    OPENAI_API_KEY: SecretStr = SecretStr("")
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_TIMEOUT: float = 10.0

    # Application
    environment: str = "local"
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000
    # quantity of workers for uvicorn
    workers_count: int = 1

    log_level: LogLevel = LogLevel.INFO
    
    # Security
    secret_key: SecretStr = SecretStr("")
    
    # CORS
    allowed_origins: str = "http://localhost:3000,http://localhost:8080,http://127.0.0.1:3000"
    backend_cors_origins_str: str = "http://localhost,http://127.0.0.1,https://localhost,https://127.0.0.1"
    
    # Sentry's configuration.
    sentry_dsn: Optional[str] = None
    sentry_sample_rate: float = 1.0

    # ✅ Declare constant as ClassVar
    DEFAULT_LANGUAGE_CODE: ClassVar[str] = "en"

    reload: bool = True if environment == "local" else False

    MCP_SERVER_CONFIG_PATH: Path = Path("core/config/server_config.json")

    DB_URL: str = ""

    @property
    def backend_cors_origins(self) -> List[str]:
        """Parse backend CORS origins from comma-separated string"""
        return [origin.strip() for origin in self.backend_cors_origins_str.split(",") if origin.strip()]

    model_config = SettingsConfigDict(
        env_file=str(env_path),
        env_file_encoding="utf-8",
        extra="ignore",  # Ignore extra fields
        case_sensitive=False,  # Allow lowercase env vars
    )


# Global settings instance
settings = Settings()
