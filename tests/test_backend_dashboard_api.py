from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.services.matching_service import overview_from_overnight


client = TestClient(app)


def test_health_and_security_headers():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["content-security-policy"].startswith("default-src 'self'")


def test_figures_endpoint_includes_data_distribution():
    for path in ("/api/v1/analytics/figures", "/api/figures/list"):
        response = client.get(path)
        assert response.status_code == 200
        filenames = {item["filename"] for item in response.json()}
        assert "figure6_data_distribution.png" in filenames


def test_overview_uses_promotion_and_best_validation_checkpoint():
    payload = {
        "decision": {"selected": "exact", "reason": "Safe batch default."},
        "training_runs": {
            "ppo": [
                {"timesteps": 500_000, "validation_metrics": {"mean_compatibility": 0.04}},
                {"timesteps": 1_000_000, "validation_metrics": {"mean_compatibility": 0.055}},
                {"timesteps": 2_000_000, "validation_metrics": {"mean_compatibility": 0.05}},
            ]
        },
    }

    overview = overview_from_overnight(payload)

    assert overview == {
        "promoted_engine": "exact",
        "promoted_reason": "Safe batch default.",
        "top_rl_engine": "ppo_maskable",
        "top_rl_steps": 1_000_000,
        "top_rl_compatibility": 0.055,
    }
