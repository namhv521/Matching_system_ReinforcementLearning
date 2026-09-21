import pytest

from src.analysis.experiment_analysis import summarize_results
from scripts.build_public_data import sanitize_theses


def test_summarize_results_aggregates_algorithms_across_seeds():
    payloads = [
        {
            "plan": {"seed": 42},
            "results": [
                {"algorithm": "exact", "mean_compatibility": 0.06, "invalid_proposals": 0, "quota_violations": 0},
                {"algorithm": "ppo_maskable", "mean_compatibility": 0.04, "invalid_proposals": 0, "quota_violations": 0},
            ],
        },
        {
            "plan": {"seed": 123},
            "results": [
                {"algorithm": "exact", "mean_compatibility": 0.08, "invalid_proposals": 0, "quota_violations": 0},
                {"algorithm": "ppo_maskable", "mean_compatibility": 0.06, "invalid_proposals": 0, "quota_violations": 0},
            ],
        },
    ]

    summary = summarize_results(payloads)

    assert summary["seeds"] == [42, 123]
    assert summary["algorithms"]["exact"]["runs"] == 2
    assert summary["algorithms"]["exact"]["mean_compatibility"] == pytest.approx(0.07)
    assert summary["algorithms"]["exact"]["std_compatibility"] == pytest.approx(0.0141421356)
    assert summary["algorithms"]["ppo_maskable"]["safe_run_rate"] == 1.0


def test_summarize_results_rejects_missing_metrics():
    payload = {"plan": {"seed": 42}, "results": [{"algorithm": "ppo_maskable"}]}

    with pytest.raises(ValueError, match="missing required metrics"):
        summarize_results([payload])


def test_sanitize_theses_removes_student_identity():
    rows = [
        {"student_id": "11230001", "student_name": "Nguyen Van A", "thesis_title": "AI", "advisor_name": "TS B"},
        {"student_id": "11230002", "student_name": "Tran Thi C", "thesis_title": "Web", "advisor_name": "TS D"},
    ]

    sanitized = sanitize_theses(rows)

    assert sanitized[0]["student_id"] == "STU-0001"
    assert sanitized[0]["student_name"] == "Sinh viên 0001"
    assert "11230001" not in str(sanitized)
    assert "Nguyen Van A" not in str(sanitized)
    assert sanitized[1]["thesis_title"] == "Web"
