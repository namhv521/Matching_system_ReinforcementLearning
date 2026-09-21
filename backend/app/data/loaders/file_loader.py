"""File loading utilities for local curated datasets and experiment results."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List
import pandas as pd

from backend.app.core.config import settings
from backend.app.core.logging import logger


class FileDataLoader:
    def __init__(self, data_dir: Path | None = None, results_dir: Path | None = None):
        self.data_dir = data_dir or settings.DATA_DIR
        self.results_dir = results_dir or settings.RESULTS_DIR

    def load_csv(self, filename: str) -> pd.DataFrame:
        fpath = self.data_dir / filename
        if not fpath.exists():
            raise FileNotFoundError(f"Curated dataset file not found: {fpath}")
        try:
            return pd.read_csv(fpath, encoding="utf-8-sig")
        except UnicodeDecodeError:
            return pd.read_csv(fpath, encoding="utf-8")

    def load_json(self, fpath: Path | str) -> Any:
        path = Path(fpath)
        if not path.is_absolute():
            path = self.data_dir / path
        if not path.exists():
            raise FileNotFoundError(f"JSON file not found: {path}")
        return json.loads(path.read_text(encoding="utf-8"))

    def load_all_curated(self) -> Dict[str, pd.DataFrame]:
        logger.info(f"Loading curated datasets from {self.data_dir}")
        return {
            "advisors": self.load_csv("advisors.csv"),
            "lecturers": self.load_csv("lecturers.csv"),
            "theses": self.load_csv("theses.csv"),
            "student_profiles": self.load_csv("student_profiles.csv"),
            "courses": self.load_csv("courses.csv"),
            "advisor_skill_evidence": self.load_csv("advisor_skill_evidence.csv"),
            "advisor_identity_map": self.load_csv("advisor_identity_map.csv"),
        }

    def load_quality_report(self) -> Dict[str, Any]:
        qfile = self.data_dir / "quality_report.json"
        if qfile.exists():
            return self.load_json(qfile)
        return {}

    def load_benchmark_results(self, seed: int = 42) -> List[Dict[str, Any]]:
        overnight_file = self.results_dir / f"overnight_seed{seed}_steps2000000.json"
        if overnight_file.exists():
            data = self.load_json(overnight_file)
            return data.get("results", [])
        return []

    def load_training_curves(self, seed: int = 42) -> Dict[str, List[Dict[str, Any]]]:
        milestones = [500_000, 1_000_000, 2_000_000]
        algos = ["ppo", "a2c", "dqn", "qrdqn"]
        curves: Dict[str, List[Dict[str, Any]]] = {algo: [] for algo in algos}
        for algo in algos:
            for m in milestones:
                fpath = self.results_dir / f"{algo}_seed{seed}_steps{m}.json"
                if fpath.exists():
                    data = self.load_json(fpath)
                    curves[algo].append({
                        "milestone": m,
                        "train_reward": data.get("train_metrics", {}).get("total_reward", 0.0),
                        "val_reward": data.get("validation_metrics", {}).get("total_reward", 0.0),
                        "train_compatibility": data.get("train_metrics", {}).get("mean_compatibility", 0.0),
                        "val_compatibility": data.get("validation_metrics", {}).get("mean_compatibility", 0.0),
                        "invalid_proposals": data.get("validation_metrics", {}).get("invalid_proposals", 0),
                    })
        return curves
