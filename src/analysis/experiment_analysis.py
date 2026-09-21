"""Aggregate verified overnight benchmark artifacts across random seeds."""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from statistics import mean, stdev
from typing import Any, Iterable

REQUIRED_METRICS = ("algorithm", "mean_compatibility", "invalid_proposals", "quota_violations")


def load_payloads(results_dir: Path) -> list[dict[str, Any]]:
    paths = sorted(results_dir.glob("overnight_seed*_steps*.json"))
    if not paths:
        raise FileNotFoundError(f"No overnight result files found in {results_dir}")
    return [json.loads(path.read_text(encoding="utf-8")) for path in paths]


def summarize_results(payloads: Iterable[dict[str, Any]]) -> dict[str, Any]:
    seeds: set[int] = set()
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for payload in payloads:
        seed = payload.get("plan", {}).get("seed")
        if seed is None:
            raise ValueError("Result payload is missing plan.seed")
        seeds.add(int(seed))
        for row in payload.get("results", []):
            missing = [name for name in REQUIRED_METRICS if name not in row]
            if missing:
                raise ValueError(f"Result row is missing required metrics: {missing}")
            grouped[str(row["algorithm"])].append(row)

    algorithms: dict[str, dict[str, Any]] = {}
    for algorithm, rows in sorted(grouped.items()):
        scores = [float(row["mean_compatibility"]) for row in rows]
        safe = [
            int(row["invalid_proposals"]) == 0 and int(row["quota_violations"]) == 0
            for row in rows
        ]
        algorithms[algorithm] = {
            "runs": len(rows),
            "mean_compatibility": mean(scores),
            "std_compatibility": stdev(scores) if len(scores) > 1 else 0.0,
            "safe_run_rate": sum(safe) / len(safe),
            "mean_invalid_proposals": mean(float(row["invalid_proposals"]) for row in rows),
            "mean_quota_violations": mean(float(row["quota_violations"]) for row in rows),
        }
    return {"seeds": sorted(seeds), "algorithms": algorithms}


def write_summary(results_dir: Path, output: Path) -> dict[str, Any]:
    summary = summarize_results(load_payloads(results_dir))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return summary
