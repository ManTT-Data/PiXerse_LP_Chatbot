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
    OPENAI_MODEL: str = ""
    OPENAI_TIMEOUT: float = 0.0

    # Application
    environment: str = ""
    debug: bool = False
    host: str = ""
    port: int = 0
    # quantity of workers for uvicorn
    workers_count: int = 0

    log_level: LogLevel = LogLevel.INFO
    
    # Security
    secret_key: SecretStr = SecretStr("")
    
    # CORS
    allowed_origins: str = ""
    backend_cors_origins_str: str = ""
    
    # Sentry's configuration.
    sentry_dsn: Optional[str] = None
    sentry_sample_rate: float = 0.0

    # ✅ Declare constant as ClassVar
    DEFAULT_LANGUAGE_CODE: ClassVar[str] = "en"

    reload: bool = False

    MCP_SERVER_CONFIG_PATH: str = ""

    DB_URL: str = ""

    @property
    def backend_cors_origins(self) -> List[str]:
        """Parse backend CORS origins from comma-separated string"""
        if not self.backend_cors_origins_str:
            return []
        return [origin.strip() for origin in self.backend_cors_origins_str.split(",") if origin.strip()]
    
    @property 
    def mcp_server_config_path(self) -> Path:
        """Convert MCP server config path string to Path object"""
        if not self.MCP_SERVER_CONFIG_PATH:
            return Path("core/config/server_config.json")
        return Path(self.MCP_SERVER_CONFIG_PATH)

    model_config = SettingsConfigDict(
        env_file=str(env_path),
        env_file_encoding="utf-8",
        extra="ignore",  # Ignore extra fields
        case_sensitive=False,  # Allow lowercase env vars
    )


# Global settings instance
settings = Settings()
