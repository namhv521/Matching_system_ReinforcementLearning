"""Pydantic schemas for Dual-Engine Cohort Matching and Advisor Recommendation."""
from __future__ import annotations

from typing import Any, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class MatchCohortRequest(BaseModel):
    split: str = Field(
        default="validation",
        description="Dataset split partition: 'validation', 'test', or 'train'",
    )
    algorithm: str = Field(
        default="exact",
        description="Algorithm: exact, ppo, ppo_maskable, gale_shapley, greedy, random",
    )


class CohortAssignmentSchema(BaseModel):
    step: int
    student_id: str
    student_name: str
    thesis_title: str
    field_category: str
    assigned_advisor_id: str
    assigned_advisor_name: str
    academic_title: str = ""
    compatibility_score: float
    historical_advisor: str = ""
    historical_match: bool = False

    model_config = ConfigDict(from_attributes=True)


class AdvisorWorkloadSchema(BaseModel):
    advisor_name: str
    capacity: int
    assigned: int
    remaining: int
    utilization_pct: float

    model_config = ConfigDict(from_attributes=True)


class CohortMatchMetrics(BaseModel):
    mean_compatibility: float
    total_reward: Optional[float] = None
    constraint_violations: int = 0
    quota_violations: int = 0
    invalid_proposals: int = 0
    gini_index: float = 0.0
    execution_time_ms: float = 0.0
    accuracy_vs_historical: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)


class CohortMatchResponse(BaseModel):
    algorithm: str
    split: str
    cohort_size: int
    metrics: CohortMatchMetrics
    assignments: List[CohortAssignmentSchema]
    workload_distribution: List[AdvisorWorkloadSchema]


class RecommendRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=1000, description="Thesis title or research topic")
    field: Optional[str] = Field(default="", max_length=200, description="Field or domain (e.g. AI, Web, Mobile)")
    tech_stack: Optional[str] = Field(default="", max_length=500, description="Technologies, languages, frameworks")
    top_k: int = Field(default=5, ge=1, le=20, description="Number of advisors to recommend")


class AdvisorRecommendation(BaseModel):
    rank: int
    advisor_id: str
    advisor_name: str
    academic_title: str = ""
    primary_field: str = ""
    compatibility_score: float
    capacity: int = 5
    skills: List[str] = Field(default_factory=list)
    email: Optional[str] = ""


class RecommendResponse(BaseModel):
    query: dict[str, Any]
    top_k: int
    recommendations: List[AdvisorRecommendation]
