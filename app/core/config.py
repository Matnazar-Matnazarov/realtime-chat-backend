"""
Application configuration management.
"""

from zoneinfo import ZoneInfo

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # App
    APP_NAME: str = "Realtime Chat API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/chatdb"
    DB_ECHO: bool = False

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_PUBSUB_CHANNEL: str = "chat:messages"

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production-use-openssl-rand-hex-32"
    REFRESH_SECRET_KEY: str = "your-refresh-secret-key-change-in-production-use-openssl-rand-hex-32"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15  # 15 minutes
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7  # 7 days

    # CORS - stored as string, converted to list via computed field
    CORS_ORIGINS_STR: str = (
        "http://localhost:3000,http://localhost:5173,http://localhost:8000,http://127.0.0.1:8000"
    )

    @computed_field
    @property
    def CORS_ORIGINS(self) -> list[str]:
        """Parse CORS origins from comma-separated string."""
        if not self.CORS_ORIGINS_STR:
            return ["http://localhost:3000", "http://localhost:5173"]
        return [origin.strip() for origin in self.CORS_ORIGINS_STR.split(",") if origin.strip()]

    # OAuth2
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GITHUB_CLIENT_ID: str = ""
    GITHUB_CLIENT_SECRET: str = ""

    # File Upload
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 10485760  # 10MB
    ALLOWED_EXTENSIONS_STR: str = "image/jpeg,image/png,image/gif,image/webp,video/mp4,video/webm"

    @computed_field
    @property
    def ALLOWED_EXTENSIONS(self) -> set[str]:
        """Parse allowed extensions from comma-separated string."""
        if not self.ALLOWED_EXTENSIONS_STR:
            return {
                "image/jpeg",
                "image/png",
                "image/gif",
                "image/webp",
                "video/mp4",
                "video/webm",
            }
        return {ext.strip() for ext in self.ALLOWED_EXTENSIONS_STR.split(",") if ext.strip()}

    # Admin
    ADMIN_USERNAME: str = "admin"
    ADMIN_EMAIL: str = "admin@example.com"
    ADMIN_PASSWORD: str = "admin123"

    # Timezone
    TIMEZONE: str = "Asia/Tashkent"

    @computed_field
    @property
    def TZ_INFO(self) -> ZoneInfo:
        """Get timezone info."""
        return ZoneInfo(self.TIMEZONE)


settings = Settings()
