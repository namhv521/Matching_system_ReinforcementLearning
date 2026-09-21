"""Quality gate for deciding whether an RL policy should replace exact matching."""
from __future__ import annotations

from collections import defaultdict
from statistics import mean, pstdev
from typing import Mapping, Sequence


def aggregate_runs(payloads: Sequence[Mapping]) -> dict[str, dict]:
    """Aggregate compatible benchmark result payloads across random seeds."""
    grouped: dict[str, list[Mapping]] = defaultdict(list)
    for payload in payloads:
        for row in payload["results"]:
            grouped[row["algorithm"]].append(row)
    return {
        algorithm: {
            "mean_compatibility_mean": mean(row["mean_compatibility"] for row in rows),
            "mean_compatibility_std": pstdev(row["mean_compatibility"] for row in rows),
            "load_variance_mean": mean(row["load_variance"] for row in rows),
            "quota_violations": sum(row.get("quota_violations", 0) for row in rows),
            "invalid_proposals": sum(row.get("invalid_proposals", 0) for row in rows),
            "runs": len(rows),
        }
        for algorithm, rows in grouped.items()
    }


def select_engine(summary: Mapping[str, Mapping], min_improvement: float = 0.01) -> dict:
    """Select exact by default; promote PPO only for a real, safe improvement."""
    eligible = {
        name: metrics for name, metrics in summary.items()
        if metrics.get("quota_violations", 0) == 0 and metrics.get("invalid_proposals", 0) == 0
    }
    if not eligible:
        return {"passed": False, "selected": None, "reason": "No engine satisfied hard constraints."}
    exact = eligible.get("exact")
    ppo = eligible.get("ppo_maskable")
    if exact:
        if ppo and ppo["mean_compatibility_mean"] >= exact["mean_compatibility_mean"] + min_improvement:
            return {"passed": True, "selected": "ppo_maskable", "reason": "PPO beat exact by the configured validation margin."}
        return {"passed": True, "selected": "exact", "reason": "Exact is the safe batch-matching default."}
    selected = max(eligible, key=lambda name: eligible[name]["mean_compatibility_mean"])
    return {"passed": True, "selected": selected, "reason": "Exact was unavailable; selected the best safe fallback."}
