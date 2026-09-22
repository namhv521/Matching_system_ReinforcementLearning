"""Database engine and session management."""
from __future__ import annotations

from pathlib import Path
from typing import Generator
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.db.base import Base

connect_args = {}
is_postgresql = settings.DATABASE_URL.startswith("postgresql")
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine_options = {
    "connect_args": connect_args,
    "echo": settings.DEBUG,
}
if is_postgresql:
    engine_options.update(
        pool_pre_ping=True,
        pool_size=3,
        max_overflow=2,
        pool_recycle=300,
    )

engine = create_engine(settings.DATABASE_URL, **engine_options)
if settings.DATABASE_URL.startswith("sqlite") and engine.url.database not in (None, ":memory:"):
    Path(engine.url.database).parent.mkdir(parents=True, exist_ok=True)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=Session,
)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Initialize database tables idempotently."""
    logger.info("Initializing database schema...")
    # Import all models to ensure metadata registration
    import backend.app.models  # noqa: F401
    Base.metadata.create_all(bind=engine)
    logger.info("Database schema initialized successfully.")


def probe_database() -> bool:
    """Return whether the configured database accepts a minimal query."""
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except Exception:
        logger.warning("Database health probe failed.")
        return False


def database_health() -> dict[str, str]:
    """Provide a public database health summary without connection details."""
    if probe_database():
        return {"status": "ok", "database": "connected"}
    return {"status": "degraded", "database": "unavailable"}
