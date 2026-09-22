"""Centralized Application Configuration using Pydantic Settings."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, List, Union
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parents[3]


def normalize_database_url(value: str) -> str:
    """Use SQLAlchemy's psycopg dialect and require TLS for PostgreSQL."""
    url = value.strip()
    if url.startswith("postgres://"):
        url = f"postgresql://{url.removeprefix('postgres://')}"
    if url.startswith("postgresql://"):
        url = f"postgresql+psycopg://{url.removeprefix('postgresql://')}"
    if not url.startswith("postgresql+psycopg://"):
        return url

    parsed = urlsplit(url)
    query = [
        (key, item)
        for key, item in parse_qsl(parsed.query, keep_blank_values=True)
        if key.lower() != "sslmode"
    ]
    query.append(("sslmode", "require"))
    return urlunsplit(parsed._replace(query=urlencode(query)))


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ROOT_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Core Application Settings
    APP_NAME: str = "KLTN Thesis-Advisor Allocation Decision Support API"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # Database Settings
    DATABASE_URL: str = Field(
        default=f"sqlite:///{ROOT_DIR / 'data' / 'storage' / 'kltn_matching.db'}",
        description="SQLAlchemy Database Connection URI (SQLite for local dev, PostgreSQL for production)",
    )

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def normalize_database_connection(cls, value: str) -> str:
        return normalize_database_url(value)

    # MongoDB Settings (Optional / Pre-configured)
    MONGODB_ENABLED: bool = False
    MONGODB_URI: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "kltn_matching"

    # CORS Settings
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [i.strip() for i in v.split(",") if i.strip()]
        return v

    # Machine Learning & Decision Support
    MATCHING_SEED: int = 42
    MATCHING_TEXT_BACKEND: str = "tfidf"
    ALLOW_FILE_FALLBACK: bool = False

    # Directory Paths
    ROOT_PATH: Path = ROOT_DIR
    DATA_DIR: Path = ROOT_DIR / "data" / "curated"
    RAW_DATA_DIR: Path = ROOT_DIR / "data" / "raw"
    RESULTS_DIR: Path = ROOT_DIR / "outputs" / "results"
    MODELS_DIR: Path = ROOT_DIR / "outputs" / "models"
    FIGURES_DIR: Path = ROOT_DIR / "outputs" / "figures"
    FRONTEND_DIR: Path = ROOT_DIR / "frontend"
    DIST_DIR: Path = ROOT_DIR / "frontend" / "dist"


settings = Settings()
