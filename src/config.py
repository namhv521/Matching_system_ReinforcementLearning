"""Configuration settings for KLTN AI Agent using Pydantic Settings."""

import os
from pathlib import Path
from typing import List, Literal, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class AgentSettings(BaseSettings):
    """AI Agent and LLM configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Core App
    APP_NAME: str = "KLTN AI Advisor Matching Agent"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # LLM Settings
    LLM_PROVIDER: str = "mock"
    LLM_MODEL_NAME: str = "gpt-4o-mini"
    LLM_TEMPERATURE: float = 0.2
    LLM_MAX_TOKENS: int = 2048

    # API Keys (Optional with mock fallback)
    OPENAI_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None

    # Agent Strategy & Bounds
    MAX_ITERATIONS: int = 5
    ENABLE_STREAMING: bool = True
    SIMILARITY_THRESHOLD: float = 0.65

    # Storage & Persistence
    DATA_DIR: Path = Path(__file__).resolve().parents[1] / "data" / "curated"
    LOGS_DIR: Path = Path(__file__).resolve().parents[1] / "logs"
    DATABASE_URL: str = "sqlite:///./data/storage/kltn_matching.db"
    MONGODB_ENABLED: bool = False
    MONGODB_URI: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "kltn_matching"

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8000",
        "http://localhost:8501",  # Streamlit
    ]


agent_settings = AgentSettings()
