"""
Centralized configuration for TasteMaker backend.

Uses Pydantic settings to read from environment variables with sensible defaults.
Supports both simple local deployment (SQLite, single-user) and production (PostgreSQL, multi-user).
"""
import os
import secrets
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # ==========================================================================
    # Database
    # ==========================================================================
    database_url: str = "sqlite:///./tastemaker.db"

    # ==========================================================================
    # Authentication
    # ==========================================================================
    single_user_mode: bool = True
    secret_key: str = ""  # Auto-generated if not provided

    # JWT settings
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 days

    # ==========================================================================
    # API Keys
    # ==========================================================================
    anthropic_api_key: Optional[str] = None

    # ==========================================================================
    # Background Jobs
    # ==========================================================================
    enable_background_jobs: bool = False
    redis_url: str = "redis://localhost:6379/0"

    # ==========================================================================
    # CORS
    # ==========================================================================
    cors_origins: str = "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173"

    # ==========================================================================
    # File Storage
    # ==========================================================================
    upload_dir: Optional[str] = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        # Also check parent directory for .env (for when running from backend/src)
        extra = "ignore"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Auto-generate secret key if not provided and not in single-user mode
        if not self.secret_key and not self.single_user_mode:
            self.secret_key = secrets.token_hex(32)

    @property
    def is_sqlite(self) -> bool:
        """Check if using SQLite database."""
        return self.database_url.startswith("sqlite")

    @property
    def is_postgresql(self) -> bool:
        """Check if using PostgreSQL database."""
        return self.database_url.startswith("postgres")

    @property
    def normalized_database_url(self) -> str:
        """Get database URL with any necessary normalization."""
        url = self.database_url
        # Heroku uses postgres:// but SQLAlchemy requires postgresql://
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        return url

    @property
    def cors_origins_list(self) -> list[str]:
        """Get CORS origins as a list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    @property
    def has_anthropic_api_key(self) -> bool:
        """Check if Anthropic API key is configured."""
        return bool(self.anthropic_api_key)

    @property
    def effective_secret_key(self) -> str:
        """Get secret key, generating one if needed."""
        if self.secret_key:
            return self.secret_key
        # In single-user mode, use a consistent default
        if self.single_user_mode:
            return "tastemaker-single-user-mode-key"
        # This shouldn't happen, but fallback to random
        return secrets.token_hex(32)


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    # Try loading .env from multiple locations
    env_locations = [
        ".env",
        "../.env",
        "../../.env",
    ]

    for env_path in env_locations:
        if os.path.exists(env_path):
            return Settings(_env_file=env_path)

    return Settings()


# Convenience accessor
settings = get_settings()
