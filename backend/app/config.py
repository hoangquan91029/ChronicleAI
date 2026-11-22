import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "ChronicleAI"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Storage Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    UPLOADS_DIR: Path = DATA_DIR / "uploads"
    EXPORTS_DIR: Path = DATA_DIR / "exports"
    
    # LLM Settings
    LLM_PROVIDER: str = "auto"  # 'auto', 'gemini', 'openai', 'offline'
    GEMINI_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o"
    GEMINI_MODEL: str = "gemini-1.5-flash"
    
    # Embeddings & Chunking
    CHUNK_SIZE: int = 900  # Characters per chunk (preserves complete historical paragraph context)
    CHUNK_OVERLAP: int = 100  # Overlap characters
    MIN_CHUNK_CHARS: int = 50
    SCANNED_THRESHOLD_CHARS_PER_PAGE: int = 30  # If page has < 30 text chars but has images/drawing, flag as scanned
    
    # Vector Search
    TOP_K_DEFAULT: int = 5
    SIMILARITY_THRESHOLD: float = 0.15
    
    # CORS
    CORS_ORIGINS: list[str] = ["*"]

    model_config = SettingsConfigDict(env_file=".env", extra="allow")


settings = Settings()

# Ensure directories exist
settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
settings.UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
settings.EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
