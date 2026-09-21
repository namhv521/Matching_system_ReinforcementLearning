from src.rl.promotion import select_engine


def test_ppo_with_constraint_violation_cannot_win():
    result = select_engine({
        "exact": {"mean_compatibility_mean": 0.70, "quota_violations": 0, "invalid_proposals": 0},
        "ppo_maskable": {"mean_compatibility_mean": 0.90, "quota_violations": 1, "invalid_proposals": 0},
    })

    assert result["selected"] == "exact"
    assert result["passed"] is True


def test_ppo_requires_meaningful_improvement_over_exact():
    result = select_engine({
        "exact": {"mean_compatibility_mean": 0.70, "quota_violations": 0, "invalid_proposals": 0},
        "ppo_maskable": {"mean_compatibility_mean": 0.705, "quota_violations": 0, "invalid_proposals": 0},
    })

    assert result["selected"] == "exact"


def test_aggregate_runs_handles_optional_quota_violations():
    from src.rl.promotion import aggregate_runs

    payloads = [
        {
            "results": [
                {"algorithm": "ppo_maskable", "mean_compatibility": 0.8, "load_variance": 0.1},
                {"algorithm": "exact", "mean_compatibility": 0.85, "load_variance": 0.1, "quota_violations": 0},
            ]
        }
    ]
    summary = aggregate_runs(payloads)
    assert summary["ppo_maskable"]["quota_violations"] == 0
    assert summary["ppo_maskable"]["invalid_proposals"] == 0
    assert summary["exact"]["mean_compatibility_mean"] == 0.85
