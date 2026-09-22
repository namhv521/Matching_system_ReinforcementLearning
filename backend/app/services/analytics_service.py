"""Analytics and Decision Support metrics service."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List
from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.exceptions import DatabaseUnavailableError
from backend.app.data.loaders.file_loader import FileDataLoader
from backend.app.models.advisor import Advisor
from backend.app.models.thesis import Thesis
from backend.app.repositories.benchmark_repository import BenchmarkRepository
from backend.app.schemas.analytics import FigureItem, OverviewResponse, OverviewSplits, SystemHealthResponse
from backend.app.services.matching_service import MatchingService, get_matching_service


class AnalyticsService:
    def __init__(self, db: Session, loader: FileDataLoader | None = None):
        self.db = db
        self.loader = loader or FileDataLoader()
        self.bench_repo = BenchmarkRepository(db)

    def _matching_service(self) -> MatchingService:
        return get_matching_service(self.db)

    def get_overview(self) -> OverviewResponse:
        # Use matching service overview for full split-aligned metrics
        data = self._matching_service().get_overview()
        return OverviewResponse(
            total_theses=data["total_theses"],
            total_advisors=data["total_advisors"],
            splits=OverviewSplits(
                train=data["splits"]["train"],
                validation=data["splits"]["validation"],
                test=data["splits"]["test"],
            ),
            promoted_engine=data["promoted_engine"],
            promoted_reason=data["promoted_reason"],
            top_rl_engine=data["top_rl_engine"],
            top_rl_steps=data["top_rl_steps"],
            top_rl_compatibility=data["top_rl_compatibility"],
            seed=data["seed"],
        )

    def get_benchmarks(self) -> List[Dict[str, Any]]:
        try:
            db_records = self.bench_repo.list_benchmarks()
        except SQLAlchemyError:
            raise DatabaseUnavailableError() from None
        if db_records:
            return [
                {
                    "algorithm": r.algorithm,
                    "total_reward": r.total_reward,
                    "mean_compatibility": r.mean_compatibility,
                    "constraint_violations": r.constraint_violations,
                    "quota_violations": r.quota_violations,
                    "invalid_proposals": r.invalid_proposals,
                    "gini_index": r.gini_index,
                    "execution_time_ms": r.execution_time_ms,
                    "accuracy_vs_historical": r.accuracy_vs_historical,
                }
                for r in db_records
            ]
        return MatchingService().get_benchmarks() if settings.ALLOW_FILE_FALLBACK else []

    def get_training_curves(self) -> Dict[str, List[Dict[str, Any]]]:
        try:
            db_curves = self.bench_repo.get_training_curves()
        except SQLAlchemyError:
            raise DatabaseUnavailableError() from None
        if db_curves:
            out = {}
            for algo, points in db_curves.items():
                out[algo] = [
                    {
                        "milestone": p.milestone,
                        "train_reward": p.train_reward,
                        "val_reward": p.val_reward,
                        "train_compatibility": p.train_compatibility,
                        "val_compatibility": p.val_compatibility,
                        "invalid_proposals": p.invalid_proposals,
                    }
                    for p in points
                ]
            return out
        return MatchingService().get_training_curves() if settings.ALLOW_FILE_FALLBACK else {}

    def get_figures_list(self) -> List[FigureItem]:
        return [
            FigureItem(
                id="figure1",
                title="Figure 1: Maskable PPO Learning Dynamics",
                filename="figure1_ppo_learning_curves.png",
                caption="PPO episodic reward and compatibility convergence across 2M timesteps.",
            ),
            FigureItem(
                id="figure2",
                title="Figure 2: Action Masking vs Constraint Violations",
                filename="figure2_constraint_violations.png",
                caption="Comparison of invalid proposals and quota violations across RL architectures.",
            ),
            FigureItem(
                id="figure3",
                title="Figure 3: Comprehensive Multi-Metric Benchmark",
                filename="figure3_algorithm_comparison.png",
                caption="Benchmark of 8 algorithms across compatibility, load balance, and fairness.",
            ),
            FigureItem(
                id="figure4",
                title="Figure 4: System Architecture & Decision Flow",
                filename="figure4_system_architecture.png",
                caption="End-to-end multi-tier pipeline from raw curriculum data to optimal assignment.",
            ),
            FigureItem(
                id="figure5",
                title="Figure 5: MDP Formulation with Action Masking",
                filename="figure5_rl_mdp_flow.png",
                caption="Sequential Markov Decision Process step showing state vector, mask filter, and policy inference.",
            ),
            FigureItem(
                id="figure6",
                title="Figure 6: Phân bố dữ liệu nghiên cứu",
                filename="figure6_data_distribution.png",
                caption="Phân bố vai trò kỹ thuật của đề tài và số nhóm kỹ năng có bằng chứng của giảng viên.",
            ),
        ]

    def get_quality_report(self) -> Dict[str, Any]:
        return self.loader.load_quality_report()

    def get_system_health(self) -> SystemHealthResponse:
        db_status = "ok"
        adv_count = 0
        theses_count = 0
        try:
            adv_count = self.db.scalar(select(func.count(Advisor.advisor_id))) or 0
            theses_count = self.db.scalar(select(func.count(Thesis.record_id))) or 0
        except Exception as exc:
            db_status = f"error: {exc}"

        ppo_path = settings.MODELS_DIR / f"ppo_seed{settings.MATCHING_SEED}_steps1000000.zip"
        rl_loaded = ppo_path.exists()

        return SystemHealthResponse(
            status="ok" if db_status == "ok" else "degraded",
            version=settings.APP_VERSION,
            environment=settings.APP_ENV,
            database=db_status,
            datasets={
                "advisors": adv_count,
                "theses": theses_count,
            },
            rl_model_loaded=rl_loaded,
        )
