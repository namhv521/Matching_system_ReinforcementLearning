"""Backward-compatible endpoints matching exact frontend contract."""
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.services.matching_service import get_matching_service

compat_router = APIRouter(prefix="/api", tags=["Frontend Direct Compatibility"])


class MatchCohortRequest(BaseModel):
    split: str = Field(default="validation", description="Dataset split: validation, test, or train")
    algorithm: str = Field(default="exact", description="Algorithm: exact, ppo, ppo_maskable, gale_shapley, greedy, random")


class RecommendRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=1000, description="Thesis title or description")
    field: Optional[str] = Field(default="", max_length=200, description="Research field or domain")
    tech_stack: Optional[str] = Field(default="", max_length=500, description="Keywords, frameworks, or technologies")
    top_k: int = Field(default=5, ge=1, le=20, description="Number of advisors to recommend")


@compat_router.get("/overview")
def get_overview() -> dict[str, Any]:
    svc = get_matching_service()
    return svc.get_overview()


@compat_router.get("/benchmarks")
def get_benchmarks() -> list[dict[str, Any]]:
    svc = get_matching_service()
    return svc.get_benchmarks()


@compat_router.get("/training-curves")
def get_training_curves() -> dict[str, Any]:
    svc = get_matching_service()
    return svc.get_training_curves()


@compat_router.get("/advisors")
def get_advisors() -> list[dict[str, Any]]:
    svc = get_matching_service()
    return svc.get_advisors()


@compat_router.get("/theses")
def get_theses(
    split: str = Query("validation", pattern="^(train|validation|test)$"),
    limit: int = Query(50, ge=1, le=200),
) -> list[dict[str, Any]]:
    svc = get_matching_service()
    return svc.get_theses(split=split, limit=limit)


@compat_router.post("/match/cohort")
def match_cohort(
    req: MatchCohortRequest,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    svc = get_matching_service()
    if req.split not in ("train", "validation", "test"):
        raise HTTPException(status_code=400, detail=f"Invalid split '{req.split}'")
    valid_algos = ("exact", "ppo", "ppo_maskable", "gale_shapley", "greedy", "random")
    if req.algorithm not in valid_algos:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid algorithm '{req.algorithm}'. Must be one of {valid_algos}",
        )
    try:
        return svc.run_cohort_matching(split=req.split, algorithm=req.algorithm, db=db)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Phân bổ thất bại: {exc}")


@compat_router.post("/match/recommend")
def recommend_advisor(req: RecommendRequest) -> dict[str, Any]:
    svc = get_matching_service()
    if not req.title.strip():
        raise HTTPException(status_code=400, detail="Thesis title cannot be empty")
    recommendations = svc.recommend_single(
        title=req.title,
        field=req.field or "",
        tech_stack=req.tech_stack or "",
        top_k=req.top_k,
    )
    return {
        "query": {
            "title": req.title,
            "field": req.field,
            "tech_stack": req.tech_stack,
        },
        "top_k": req.top_k,
        "recommendations": recommendations,
    }


@compat_router.get("/figures/list")
def list_figures() -> list[dict[str, str]]:
    return [
        {
            "id": "figure1",
            "title": "Figure 1: Maskable PPO Learning Dynamics",
            "filename": "figure1_ppo_learning_curves.png",
            "caption": "PPO episodic reward and compatibility convergence across 2M timesteps.",
        },
        {
            "id": "figure2",
            "title": "Figure 2: Action Masking vs Constraint Violations",
            "filename": "figure2_constraint_violations.png",
            "caption": "Comparison of invalid proposals and quota violations across RL architectures.",
        },
        {
            "id": "figure3",
            "title": "Figure 3: Comprehensive Multi-Metric Benchmark",
            "filename": "figure3_algorithm_comparison.png",
            "caption": "Benchmark of 8 algorithms across compatibility, load balance, and fairness.",
        },
        {
            "id": "figure4",
            "title": "Figure 4: System Architecture & Decision Flow",
            "filename": "figure4_system_architecture.png",
            "caption": "End-to-end multi-tier pipeline from raw curriculum data to optimal assignment.",
        },
        {
            "id": "figure5",
            "title": "Figure 5: MDP Formulation with Action Masking",
            "filename": "figure5_rl_mdp_flow.png",
            "caption": "Sequential Markov Decision Process step showing state vector, mask filter, and policy inference.",
        },
        {
            "id": "figure6",
            "title": "Figure 6: Phân bố dữ liệu nghiên cứu",
            "filename": "figure6_data_distribution.png",
            "caption": "Phân bố vai trò kỹ thuật của đề tài và số nhóm kỹ năng có bằng chứng của giảng viên.",
        },
    ]
