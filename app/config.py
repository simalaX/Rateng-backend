"""
Application settings.

All values can be overridden with environment variables (or a local .env
file when developing). See .env.example for the full list.
"""
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- Database -----------------------------------------------------
    DATABASE_URL: str = "postgresql://postgres:Timex88@localhost:5432/Rateng"

    # --- Auth / JWT -----------------------------------------------------
    JWT_SECRET_KEY: str = "c47a9c17d8e040909592ec8aa0fd48f9"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # --- Cloudinary (image storage) -------------------------------------
    CLOUDINARY_CLOUD_NAME: str = "llzolwc7"
    CLOUDINARY_API_KEY: str = "985572761315456"
    CLOUDINARY_API_SECRET: str = "wgT3X2kkqBE4djU_C0yuxo0Z1Ws"

    # --- Default admin, used only to seed the first login ---------------
    # Both values must be set in .env file (no defaults for security)
    ADMIN_EMAIL: str = "admin@ratengconstruction.com"
    ADMIN_PASSWORD: str = "ChangeMe123!"

    # --- CORS -------------------------------------------------------------
    # Comma-separated list of origins allowed to call this API
    CORS_ORIGINS: str = "http://localhost:3000,https://ratengconstructioninteriors.co.ke"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def sqlalchemy_database_url(self) -> str:
        """Render (and some other hosts) hand out `postgres://` URLs, which
        SQLAlchemy 2.x no longer accepts. Normalize to `postgresql://`."""
        url = self.DATABASE_URL
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        return url

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


settings = Settings()