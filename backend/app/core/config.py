import secrets
import warnings
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App
    APP_NAME: str = "AI Career Advisor"
    APP_VERSION: str = "1.0.0"
    # Controls docs exposure and error verbosity — must be False in production.
    DEBUG: bool = False
    SQL_ECHO: bool = False  # set to True to log every SQL statement

    # Database — SQLite for instant zero-dependency execution, customizable via env
    DATABASE_URL: str = "sqlite+aiosqlite:///./career_advisor.db"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT — no baked-in default. If the env var is missing we generate a
    # random one at process start (see below) rather than shipping a secret
    # that's sitting in every clone of this repo.
    SECRET_KEY: Optional[str] = None
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS — comma-separated list of allowed origins, e.g.
    # "https://your-app.vercel.app,https://your-app.netlify.app"
    # Defaults to localhost so `npm run dev` keeps working out of the box.
    CORS_ORIGINS_RAW: str = "http://localhost:5173,http://127.0.0.1:5173"

    # AI — Gemini (Google) and/or OpenRouter (OpenAI-compatible gateway).
    # If OPENROUTER_API_KEY is set it takes precedence; otherwise Gemini is used;
    # otherwise the app falls back to deterministic local heuristics.
    GEMINI_API_KEY: Optional[str] = None
    OPENROUTER_API_KEY: Optional[str] = None
    OPENROUTER_MODEL: str = "meta-llama/llama-3.3-70b-instruct"

    # Storage
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE_MB: int = 10

    # When True, the app seeds its catalog + demo users on startup. Handy on
    # hosts with ephemeral disks (free tiers) where there's no shell to run the
    # seed scripts manually. All seeds are idempotent, so this is safe to leave
    # on. Off by default so local runs don't seed unexpectedly.
    SEED_ON_STARTUP: bool = False

    class Config:
        env_file = ".env"
        case_sensitive = True

    @property
    def CORS_ORIGINS(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS_RAW.split(",") if origin.strip()]


settings = Settings()

if not settings.SECRET_KEY:
    if settings.DEBUG:
        # Dev convenience: a random key that's stable for this process, so
        # local hot-reloads don't invalidate every session on every save.
        settings.SECRET_KEY = secrets.token_urlsafe(48)
        warnings.warn(
            "SECRET_KEY not set — using a randomly generated development key. "
            "Set SECRET_KEY in your environment before deploying.",
            RuntimeWarning,
        )
    else:
        raise RuntimeError(
            "SECRET_KEY environment variable is required when DEBUG=False. "
            "Generate one with: python -c \"import secrets; print(secrets.token_urlsafe(48))\""
        )
