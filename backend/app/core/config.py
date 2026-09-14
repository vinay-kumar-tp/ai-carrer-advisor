from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # App
    APP_NAME: str = "AI Career Advisor"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    SQL_ECHO: bool = False  # set to True to log every SQL statement

    # Database — SQLite for instant zero-dependency execution, customizable via env
    DATABASE_URL: str = "sqlite+aiosqlite:///./career_advisor.db"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production-min-32-chars"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"]

    # AI — Gemini (Google) and/or OpenRouter (OpenAI-compatible gateway).
    # If OPENROUTER_API_KEY is set it takes precedence; otherwise Gemini is used;
    # otherwise the app falls back to deterministic local heuristics.
    GEMINI_API_KEY: Optional[str] = None
    OPENROUTER_API_KEY: Optional[str] = None
    OPENROUTER_MODEL: str = "meta-llama/llama-3.3-70b-instruct"

    # Storage
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE_MB: int = 10

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
