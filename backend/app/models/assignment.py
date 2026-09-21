"""SQLAlchemy models for Allocation Simulations, Assignments, and Advisor Workload."""
from __future__ import annotations

import uuid
from typing import List, Optional
from sqlalchemy import Boolean, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.base import Base, TimestampMixin


class CohortRun(Base, TimestampMixin):
    __tablename__ = "cohort_runs"

    id: Mapped[str] = mapped_column(
        String(50), primary_key=True, default=lambda: f"run-{uuid.uuid4().hex[:12]}"
    )
    algorithm: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    split: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    cohort_size: Mapped[int] = mapped_column(Integer, nullable=False)
    mean_compatibility: Mapped[float] = mapped_column(Float, nullable=False)
    quota_violations: Mapped[int] = mapped_column(Integer, default=0)
    invalid_proposals: Mapped[int] = mapped_column(Integer, default=0)
    gini_index: Mapped[float] = mapped_column(Float, default=0.0)
    execution_time_ms: Mapped[float] = mapped_column(Float, default=0.0)
    total_reward: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    accuracy_vs_historical: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Relationships
    assignments: Mapped[List["AssignmentRecord"]] = relationship(
        "AssignmentRecord", back_populates="cohort_run", cascade="all, delete-orphan"
    )
    workloads: Mapped[List["AdvisorWorkloadRecord"]] = relationship(
        "AdvisorWorkloadRecord", back_populates="cohort_run", cascade="all, delete-orphan"
    )


class AssignmentRecord(Base):
    __tablename__ = "assignment_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cohort_run_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("cohort_runs.id", ondelete="CASCADE"), index=True
    )
    step: Mapped[int] = mapped_column(Integer, nullable=False)
    student_id: Mapped[str] = mapped_column(String(50), nullable=False)
    student_name: Mapped[str] = mapped_column(String(150), nullable=False)
    thesis_title: Mapped[str] = mapped_column(String(500), nullable=False)
    field_category: Mapped[str] = mapped_column(String(100), nullable=False)
    assigned_advisor_id: Mapped[str] = mapped_column(String(100), nullable=False)
    assigned_advisor_name: Mapped[str] = mapped_column(String(200), nullable=False)
    academic_title: Mapped[str] = mapped_column(String(50), default="")
    compatibility_score: Mapped[float] = mapped_column(Float, nullable=False)
    historical_advisor: Mapped[str] = mapped_column(String(200), default="")
    historical_match: Mapped[bool] = mapped_column(Boolean, default=False)

    cohort_run: Mapped["CohortRun"] = relationship("CohortRun", back_populates="assignments")


class AdvisorWorkloadRecord(Base):
    __tablename__ = "advisor_workload_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cohort_run_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("cohort_runs.id", ondelete="CASCADE"), index=True
    )
    advisor_name: Mapped[str] = mapped_column(String(200), nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    assigned: Mapped[int] = mapped_column(Integer, nullable=False)
    remaining: Mapped[int] = mapped_column(Integer, nullable=False)
    utilization_pct: Mapped[float] = mapped_column(Float, default=0.0)

    cohort_run: Mapped["CohortRun"] = relationship("CohortRun", back_populates="workloads")
