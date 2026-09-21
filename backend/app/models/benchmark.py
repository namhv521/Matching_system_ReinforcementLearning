"""SQLAlchemy models for Algorithm Benchmarks and RL Training Curves."""
from __future__ import annotations

from typing import Optional
from sqlalchemy import Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.base import Base, TimestampMixin


class BenchmarkMetricRecord(Base, TimestampMixin):
    __tablename__ = "benchmark_metrics"

    algorithm: Mapped[str] = mapped_column(String(50), primary_key=True)
    total_reward: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    mean_compatibility: Mapped[float] = mapped_column(Float, nullable=False)
    constraint_violations: Mapped[int] = mapped_column(Integer, default=0)
    quota_violations: Mapped[int] = mapped_column(Integer, default=0)
    invalid_proposals: Mapped[int] = mapped_column(Integer, default=0)
    gini_index: Mapped[float] = mapped_column(Float, default=0.0)
    execution_time_ms: Mapped[float] = mapped_column(Float, default=0.0)
    accuracy_vs_historical: Mapped[Optional[float]] = mapped_column(Float, nullable=True)


class TrainingCurvePointRecord(Base, TimestampMixin):
    __tablename__ = "training_curve_points"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    algorithm: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    milestone: Mapped[int] = mapped_column(Integer, nullable=False)
    train_reward: Mapped[float] = mapped_column(Float, nullable=False)
    val_reward: Mapped[float] = mapped_column(Float, nullable=False)
    train_compatibility: Mapped[float] = mapped_column(Float, nullable=False)
    val_compatibility: Mapped[float] = mapped_column(Float, nullable=False)
    invalid_proposals: Mapped[int] = mapped_column(Integer, default=0)
