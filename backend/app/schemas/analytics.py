"""Pydantic schemas for System Analytics, Benchmarks, and Learning Curves."""
from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict


class OverviewSplits(BaseModel):
    train: int
    validation: int
    test: int


class OverviewResponse(BaseModel):
    total_theses: int
    total_advisors: int
    splits: OverviewSplits
    promoted_engine: str
    promoted_reason: str
    top_rl_engine: str
    top_rl_steps: int
    top_rl_compatibility: float
    seed: int


class BenchmarkItem(BaseModel):
    algorithm: str
    total_reward: Optional[float] = None
    mean_compatibility: float
    constraint_violations: int = 0
    quota_violations: int = 0
    invalid_proposals: int = 0
    gini_index: float
    execution_time_ms: float
    accuracy_vs_historical: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)


class TrainingCurvePoint(BaseModel):
    milestone: int
    train_reward: float
    val_reward: float
    train_compatibility: float
    val_compatibility: float
    invalid_proposals: int

    model_config = ConfigDict(from_attributes=True)


TrainingCurvesResponse = Dict[str, List[TrainingCurvePoint]]


class FigureItem(BaseModel):
    id: str
    title: str
    filename: str
    caption: str


class QualityReportResponse(BaseModel):
    generated_at: str
    input_thesis_rows: int
    curated_thesis_rows: int
    lecturer_count: int
    course_rows: int
    advisor_skill_rows: int
    unmatched_advisor_rows: int
    missing_advisor_success_rows: int
    unmatched_named_success_rows: int
    fuzzy_matched_rows: int
    advisor_source_name_variants: int
    advisor_canonical_used: int
    role_distribution: Dict[str, int]
    outputs: List[str]


class SystemHealthResponse(BaseModel):
    status: str
    version: str
    environment: str
    database: str
    datasets: Dict[str, int]
    rl_model_loaded: bool
