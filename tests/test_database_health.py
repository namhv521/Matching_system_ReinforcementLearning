from fastapi.testclient import TestClient

from backend.app.core.config import normalize_database_url
from backend.app.db import session
from backend.app.main import app


client = TestClient(app)


def test_postgresql_url_uses_psycopg_and_ssl():
    assert normalize_database_url("postgresql://user:password@db.example.com:5432/postgres") == (
        "postgresql+psycopg://user:password@db.example.com:5432/postgres?sslmode=require"
    )


def test_postgresql_url_requires_ssl_when_given_an_insecure_mode():
    assert normalize_database_url("postgresql+psycopg://user:password@db.example.com/postgres?sslmode=disable") == (
        "postgresql+psycopg://user:password@db.example.com/postgres?sslmode=require"
    )


def test_postgresql_url_preserves_duplicate_parameters_and_order():
    source = (
        "postgresql://user:password@db.example.com/postgres?target_session_attrs=read-write"
        "&options=-c%20statement_timeout%3D1000&options=-c%20lock_timeout%3D1000"
        "&sslmode=disable&application_name=kltn&sslmode=allow"
    )

    assert normalize_database_url(source) == (
        "postgresql+psycopg://user:password@db.example.com/postgres?target_session_attrs=read-write"
        "&options=-c+statement_timeout%3D1000&options=-c+lock_timeout%3D1000"
        "&application_name=kltn&sslmode=require"
    )


def test_health_is_ok_with_database(monkeypatch):
    monkeypatch.setattr(session, "probe_database", lambda: True)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["database"] == "connected"


def test_health_is_degraded_without_database(monkeypatch):
    monkeypatch.setattr(session, "probe_database", lambda: False)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "degraded",
        "app_name": "KLTN Thesis-Advisor Allocation Decision Support API",
        "version": "1.0.0",
        "environment": "development",
        "database": "unavailable",
    }
