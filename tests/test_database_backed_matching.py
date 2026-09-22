from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

import backend.app.models  # noqa: F401
from backend.app.db.base import Base
from backend.app.db.session import get_db
from backend.app.main import app
from backend.app.services.matching_service import MatchingService
from scripts.seed_cloud_database import seed_public_database


ROOT = Path(__file__).resolve().parents[1]


def test_database_backed_overview_uses_seeded_public_catalog():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        seed_public_database(db, ROOT / "data" / "public", ROOT / "outputs" / "results")

        service = MatchingService.from_session(db, seed=42)
        overview = service.get_overview()

    assert overview["total_theses"] == 198
    assert overview["total_advisors"] == 39
    assert service.vectorizer is None


def test_file_fallback_is_disabled_by_default(monkeypatch):
    monkeypatch.setattr("backend.app.services.matching_service.settings.ALLOW_FILE_FALLBACK", False)

    with pytest.raises(RuntimeError, match="Database-backed matching"):
        MatchingService(seed=42)


def test_compat_overview_uses_request_database_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        seed_public_database(db, ROOT / "data" / "public", ROOT / "outputs" / "results")

    def test_db():
        with Session(engine) as db:
            yield db

    app.dependency_overrides[get_db] = test_db
    try:
        response = TestClient(app).get("/api/overview")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["total_theses"] == 198
    assert response.json()["total_advisors"] == 39
