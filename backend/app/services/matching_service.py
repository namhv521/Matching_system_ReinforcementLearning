"""Core matching service for the Thesis-Advisor Allocation System."""
from __future__ import annotations

import json
import threading
import time
from pathlib import Path
from typing import Any, Optional

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.repositories.assignment_repository import AssignmentRepository
from src.environment.matching_core import ADVISOR_TEXT_COLUMNS, _row_text, build_compatibility
from src.rl.benchmark import baseline, deferred_acceptance, metrics, optimal_assignment
from src.rl.train import load_checkpoint, load_environments

ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = settings.DATA_DIR
RESULTS_DIR = settings.RESULTS_DIR
MODELS_DIR = settings.MODELS_DIR


def overview_from_overnight(payload: dict[str, Any]) -> dict[str, Any]:
    decision = payload.get("decision", {})
    ppo_runs = payload.get("training_runs", {}).get("ppo", [])
    best_ppo = max(
        ppo_runs,
        key=lambda run: float(run.get("validation_metrics", {}).get("mean_compatibility", float("-inf"))),
        default={},
    )
    return {
        "promoted_engine": decision.get("selected", "exact"),
        "promoted_reason": decision.get("reason", "Chưa có promotion decision hợp lệ."),
        "top_rl_engine": "ppo_maskable",
        "top_rl_steps": int(best_ppo.get("timesteps", 0)),
        "top_rl_compatibility": float(best_ppo.get("validation_metrics", {}).get("mean_compatibility", 0.0)),
    }


class MatchingService:
    def __init__(self, seed: int = settings.MATCHING_SEED):
        self.seed = seed
        self.advisors_df = pd.read_csv(DATA_DIR / "advisors.csv")
        self.theses_df = pd.read_csv(DATA_DIR / "theses.csv")
        self.envs, self.frames, self.advisors_clean, self.split_metadata = load_environments(seed)

        _, self.vectorizer = build_compatibility(self.frames["train"], self.advisors_clean, backend="tfidf")
        advisor_texts = _row_text(self.advisors_clean, ADVISOR_TEXT_COLUMNS)
        self.advisor_vectors = self.vectorizer.transform(advisor_texts)

        self.ppo_model = None
        self._lock = threading.Lock()

        self.overnight_data = {}
        overnight_file = RESULTS_DIR / f"overnight_seed{seed}_steps2000000.json"
        if overnight_file.exists():
            self.overnight_data = json.loads(overnight_file.read_text(encoding="utf-8"))

    def get_overview(self) -> dict[str, Any]:
        model_overview = overview_from_overnight(self.overnight_data)
        return {
            "total_theses": len(self.theses_df),
            "total_advisors": len(self.advisors_clean),
            "splits": {
                "train": len(self.frames["train"]),
                "validation": len(self.frames["validation"]),
                "test": len(self.frames["test"]),
            },
            **model_overview,
            "seed": self.seed,
        }

    def get_benchmarks(self) -> list[dict[str, Any]]:
        if "results" in self.overnight_data:
            return self.overnight_data["results"]
        return []

    def get_training_curves(self) -> dict[str, Any]:
        milestones = [500_000, 1_000_000, 2_000_000]
        algos = ["ppo", "a2c", "dqn", "qrdqn"]
        curves = {algo: [] for algo in algos}
        for algo in algos:
            for m in milestones:
                fpath = RESULTS_DIR / f"{algo}_seed{self.seed}_steps{m}.json"
                if fpath.exists():
                    data = json.loads(fpath.read_text(encoding="utf-8"))
                    curves[algo].append({
                        "milestone": m,
                        "train_reward": data["train_metrics"]["total_reward"],
                        "val_reward": data["validation_metrics"]["total_reward"],
                        "train_compatibility": data["train_metrics"]["mean_compatibility"],
                        "val_compatibility": data["validation_metrics"]["mean_compatibility"],
                        "invalid_proposals": data["validation_metrics"].get("invalid_proposals", 0),
                    })
        return curves

    def get_advisors(self) -> list[dict[str, Any]]:
        capacities = self.envs["validation"].core.capacities
        advisors_list = []
        for idx, row in self.advisors_clean.iterrows():
            skill_val = row.get("skill_count", 0)
            skill_count = int(skill_val) if pd.notna(skill_val) else 0
            pub_val = row.get("publication_evidence_count", 0)
            pub_count = int(pub_val) if pd.notna(pub_val) else 0
            advisors_list.append({
                "advisor_id": row.get("advisor_id", f"adv-{idx}"),
                "advisor_name": row["advisor_name"],
                "academic_title": row.get("academic_title", ""),
                "primary_field": row.get("primary_field", "Computer Science"),
                "email": row.get("email", ""),
                "capacity": int(capacities[idx]),
                "skill_count": skill_count,
                "publication_count": pub_count,
                "skills": str(row.get("skill_text", "")).split()[:8],
            })
        return advisors_list

    def get_theses(self, split: str = "validation", limit: int = 50) -> list[dict[str, Any]]:
        frame = self.frames.get(split, self.frames["validation"]).head(limit)
        items = []
        for _, row in frame.iterrows():
            items.append({
                "student_id": str(row.get("student_id", "")),
                "student_name": str(row.get("student_name", "Sinh viên")),
                "thesis_title": str(row.get("thesis_title", "")),
                "field_category": str(row.get("field_category", "")),
                "completion_year": int(row.get("completion_year", 2025)) if pd.notna(row.get("completion_year")) else 2025,
                "advisor_name_historical": str(row.get("advisor_name", "")),
                "tech_stack": [str(x) for x in [row.get("web_languages"), row.get("backend_frameworks"), row.get("ai_frameworks")] if pd.notna(x) and str(x).strip() != ""],
            })
        return items

    def run_cohort_matching(
        self,
        split: str = "validation",
        algorithm: str = "exact",
        db: Optional[Session] = None,
    ) -> dict[str, Any]:
        with self._lock:
            env = self.envs.get(split, self.envs["validation"])
            frame = self.frames.get(split, self.frames["validation"])
            matrix = env.core.compatibility
            capacities = env.core.capacities
            advisors = self.advisors_clean

            start_t = time.perf_counter()
            invalid_proposals = 0

            if algorithm == "exact":
                actions = optimal_assignment(matrix, capacities)
            elif algorithm == "gale_shapley":
                actions = deferred_acceptance(matrix, capacities)
            elif algorithm == "greedy":
                actions = baseline(matrix, capacities, "greedy", self.seed)
            elif algorithm == "random":
                actions = baseline(matrix, capacities, "random", self.seed)
            elif algorithm in ("ppo", "ppo_maskable"):
                ppo_path = MODELS_DIR / f"ppo_seed{self.seed}_steps1000000.zip"
                if not ppo_path.exists():
                    raise FileNotFoundError(f"Mô hình PPO checkpoint không tìm thấy tại {ppo_path}")
                if self.ppo_model is None:
                    self.ppo_model = load_checkpoint("ppo", ppo_path, env=env)
                obs, info = env.reset(seed=self.seed)
                actions = []
                terminated = False
                truncated = False
                while not (terminated or truncated):
                    action, _ = self.ppo_model.predict(obs, action_masks=info["action_mask"], deterministic=True)
                    obs, reward, terminated, truncated, info = env.step(int(action))
                    actions.append(info.get("executed_action", int(action)))
                actions = np.asarray(actions)
                invalid_proposals = env.invalid_proposals
            else:
                raise ValueError(f"Unknown algorithm: {algorithm}")

            elapsed_ms = round((time.perf_counter() - start_t) * 1000, 2)

        advisor_ids = {name: index for index, name in enumerate(advisors["advisor_name"])}
        actual = frame["advisor_name"].map(advisor_ids).to_numpy()
        summary = metrics(actions, matrix, capacities, actual)
        summary["invalid_proposals"] = invalid_proposals
        summary["execution_time_ms"] = elapsed_ms

        assignments = []
        for i, act in enumerate(actions):
            adv_row = advisors.iloc[act]
            compat = float(matrix[i, act])
            assignments.append({
                "step": i + 1,
                "student_id": str(frame.iloc[i].get("student_id", f"STU-{i+1:03d}")),
                "student_name": str(frame.iloc[i].get("student_name", f"Sinh viên {i+1}")),
                "thesis_title": str(frame.iloc[i].get("thesis_title", "")),
                "field_category": str(frame.iloc[i].get("field_category", "")),
                "assigned_advisor_id": str(adv_row.get("advisor_id", f"adv-{act}")),
                "assigned_advisor_name": str(adv_row["advisor_name"]),
                "academic_title": str(adv_row.get("academic_title", "")),
                "compatibility_score": round(compat, 4),
                "historical_advisor": str(frame.iloc[i].get("advisor_name", "")),
                "historical_match": bool(actual[i] == act),
            })

        assigned_counts = np.bincount(actions, minlength=len(capacities))
        workload = []
        for j in range(len(capacities)):
            workload.append({
                "advisor_name": str(advisors.iloc[j]["advisor_name"]),
                "capacity": int(capacities[j]),
                "assigned": int(assigned_counts[j]),
                "remaining": int(capacities[j] - assigned_counts[j]),
                "utilization_pct": round(float(assigned_counts[j] / capacities[j] * 100), 1) if capacities[j] > 0 else 0.0,
            })

        # Persist simulation run to database if session provided
        if db is not None:
            try:
                repo = AssignmentRepository(db)
                run_data = {
                    "algorithm": algorithm,
                    "split": split,
                    "cohort_size": len(frame),
                    "mean_compatibility": float(summary.get("mean_compatibility", 0.0)),
                    "quota_violations": int(summary.get("quota_violations", 0)),
                    "invalid_proposals": invalid_proposals,
                    "gini_index": float(summary.get("gini_index", 0.0)),
                    "execution_time_ms": elapsed_ms,
                    "total_reward": float(summary.get("total_reward")) if summary.get("total_reward") is not None else None,
                    "accuracy_vs_historical": float(summary.get("accuracy_vs_historical")) if summary.get("accuracy_vs_historical") is not None else None,
                }
                repo.save_cohort_run(run_data, assignments, workload)
            except Exception as exc:
                logger.warning(f"Could not persist cohort run to database: {exc}")

        return {
            "algorithm": algorithm,
            "split": split,
            "cohort_size": len(frame),
            "metrics": summary,
            "assignments": assignments,
            "workload_distribution": workload,
        }

    def recommend_single(self, title: str, field: str = "", tech_stack: str = "", top_k: int = 5) -> list[dict[str, Any]]:
        query_text = f"{title} {field} {tech_stack}".strip()
        query_vector = self.vectorizer.transform([query_text])
        scores = cosine_similarity(query_vector, self.advisor_vectors)[0]
        scores = np.nan_to_num(scores, nan=0.0)

        top_indices = np.argsort(-scores)[:top_k]
        recommendations = []
        capacities = self.envs["validation"].core.capacities

        for rank, idx in enumerate(top_indices, start=1):
            adv_row = self.advisors_clean.iloc[idx]
            score = float(scores[idx])
            recommendations.append({
                "rank": rank,
                "advisor_id": str(adv_row.get("advisor_id", f"adv-{idx}")),
                "advisor_name": str(adv_row["advisor_name"]),
                "academic_title": str(adv_row.get("academic_title", "")),
                "primary_field": str(adv_row.get("primary_field", "")),
                "compatibility_score": round(score, 4),
                "capacity": int(capacities[idx]),
                "skills": str(adv_row.get("skill_text", "")).split()[:6],
                "email": str(adv_row.get("email", "")),
            })
        return recommendations


_matching_service = None


def get_matching_service() -> MatchingService:
    global _matching_service
    if _matching_service is None:
        _matching_service = MatchingService()
    return _matching_service
