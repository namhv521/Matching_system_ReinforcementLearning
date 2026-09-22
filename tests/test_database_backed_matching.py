import csv
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

import backend.app.models  # noqa: F401
from backend.app.api.dependencies import get_analytics_svc, get_matching_svc
from backend.app.core.exceptions import CohortPersistenceError
from backend.app.db.base import Base
from backend.app.db.session import get_db
from backend.app.main import app
from backend.app.models.assignment import AssignmentRecord, AdvisorWorkloadRecord, CohortRun
from backend.app.repositories.assignment_repository import AssignmentRepository
from backend.app.services.analytics_service import AnalyticsService
from backend.app.services import matching_service
from backend.app.services.matching_service import MatchingService, get_matching_service
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


def test_seeded_catalog_preserves_snapshot_order_for_matching():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        seed_public_database(db, ROOT / "data" / "public", ROOT / "outputs" / "results")
        service = MatchingService.from_session(db)

    with (ROOT / "data" / "public" / "advisors.csv").open(encoding="utf-8-sig", newline="") as handle:
        advisor_ids = [row["advisor_id"] for row in csv.DictReader(handle)]
    with (ROOT / "data" / "public" / "theses.csv").open(encoding="utf-8-sig", newline="") as handle:
        thesis_ids = [row["record_id"] for row in csv.DictReader(handle)]

    assert service.advisors_clean["source_ordinal"].tolist() == list(range(len(advisor_ids)))
    assert service.theses_df["source_ordinal"].tolist() == list(range(len(thesis_ids)))
    assert service.advisors_clean["advisor_id"].tolist() == advisor_ids
    assert service.theses_df["record_id"].tolist() == thesis_ids


def test_empty_database_returns_generic_json_503():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)

    def empty_db():
        with Session(engine) as db:
            yield db

    app.dependency_overrides[get_db] = empty_db
    try:
        response = TestClient(app, raise_server_exceptions=False).get("/api/overview")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 503
    assert response.headers["content-type"].startswith("application/json")
    assert response.json() == {
        "error": {
            "code": "DATABASE_UNAVAILABLE",
            "message": "Database is temporarily unavailable.",
            "details": None,
        }
    }


def test_file_fallback_requires_explicit_opt_in(monkeypatch):
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    monkeypatch.setattr(matching_service.settings, "ALLOW_FILE_FALLBACK", True)

    with Session(engine) as db:
        assert get_matching_service(db).get_overview()["total_theses"] == 198


def test_compat_analytics_reads_seeded_database_without_matching_service():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        seed_public_database(db, ROOT / "data" / "public", ROOT / "outputs" / "results")

    def test_db():
        with Session(engine) as db:
            yield db

    def unexpected_matching_service():
        raise AssertionError("analytics endpoint must not read matching result files")

    app.dependency_overrides[get_db] = test_db
    app.dependency_overrides[get_matching_svc] = unexpected_matching_service
    try:
        client = TestClient(app)
        benchmarks = client.get("/api/benchmarks")
        curves = client.get("/api/training-curves")
    finally:
        app.dependency_overrides.clear()

    assert benchmarks.status_code == 200
    assert benchmarks.json()[0]["algorithm"]
    assert "accuracy_vs_historical" in benchmarks.json()[0]
    assert curves.status_code == 200
    assert curves.json()


def test_assignment_repository_commits_all_rows_or_rolls_back():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    run_data = {
        "algorithm": "exact",
        "split": "validation",
        "cohort_size": 1,
        "mean_compatibility": 0.9,
        "quota_violations": 0,
        "invalid_proposals": 0,
        "gini_index": 0.0,
        "execution_time_ms": 1.0,
        "total_reward": 0.9,
        "accuracy_vs_historical": 1.0,
    }
    assignment = {
        "step": 1,
        "student_id": "STU-0001",
        "student_name": "Sinh viên 0001",
        "thesis_title": "Test thesis",
        "field_category": "AI",
        "assigned_advisor_id": "ADV-001",
        "assigned_advisor_name": "Advisor",
        "academic_title": "TS",
        "compatibility_score": 0.9,
        "historical_advisor": "Advisor",
        "historical_match": True,
    }
    workload = {"advisor_name": "Advisor", "capacity": 1, "assigned": 1, "remaining": 0, "utilization_pct": 100.0}

    with Session(engine) as db:
        repo = AssignmentRepository(db)
        run = repo.save_cohort_run(run_data, [assignment], [workload])
        assert db.get(CohortRun, run.id) is not None
        assert len(db.scalars(select(AssignmentRecord)).all()) == 1
        assert len(db.scalars(select(AdvisorWorkloadRecord)).all()) == 1

        bad_assignment = {**assignment, "student_id": None}
        with pytest.raises(Exception):
            repo.save_cohort_run(run_data, [bad_assignment], [workload])
        assert len(db.scalars(select(CohortRun)).all()) == 1
        assert len(db.scalars(select(AssignmentRecord)).all()) == 1
        assert len(db.scalars(select(AdvisorWorkloadRecord)).all()) == 1


def test_cohort_persistence_failure_returns_controlled_error(monkeypatch):
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        seed_public_database(db, ROOT / "data" / "public", ROOT / "outputs" / "results")

    def test_db():
        with Session(engine) as db:
            yield db

    def failed_save(*args, **kwargs):
        raise RuntimeError("write failed")

    MatchingService.clear_resource_cache()
    monkeypatch.setattr(AssignmentRepository, "save_cohort_run", failed_save)
    app.dependency_overrides[get_db] = test_db
    try:
        response = TestClient(app, raise_server_exceptions=False).post(
            "/api/match/cohort", json={"split": "validation", "algorithm": "exact"}
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 503
    assert response.json()["error"]["code"] == "COHORT_PERSISTENCE_FAILED"


def test_matching_resources_are_cached_for_an_unchanged_catalog(monkeypatch):
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        seed_public_database(db, ROOT / "data" / "public", ROOT / "outputs" / "results")
        MatchingService.clear_resource_cache()
        calls = 0
        original = matching_service.build_compatibility

        def counted_build(*args, **kwargs):
            nonlocal calls
            calls += 1
            return original(*args, **kwargs)

        monkeypatch.setattr(matching_service, "build_compatibility", counted_build)
        first = MatchingService.from_session(db)
        second = MatchingService.from_session(db)
        first.recommend_single("Machine learning", top_k=1)
        first_calls = calls
        second.recommend_single("Machine learning", top_k=1)

    assert first_calls == 3
    assert calls == first_calls
