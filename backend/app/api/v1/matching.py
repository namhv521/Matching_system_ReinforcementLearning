"""Dual-Engine Matching and Recommendation endpoints for API v1."""
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.api.dependencies import get_matching_svc
from backend.app.db.session import get_db
from backend.app.repositories.assignment_repository import AssignmentRepository
from backend.app.schemas.matching import (
    CohortMatchResponse,
    MatchCohortRequest,
    RecommendRequest,
    RecommendResponse,
)
from backend.app.services.matching_service import MatchingService

router = APIRouter(prefix="/match", tags=["Dual-Engine Matching & Allocation"])


@router.post("/cohort", response_model=CohortMatchResponse)
def match_cohort(
    req: MatchCohortRequest,
    svc: MatchingService = Depends(get_matching_svc),
    db: Session = Depends(get_db),
):
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


@router.post("/recommend", response_model=RecommendResponse)
def recommend_advisor(
    req: RecommendRequest,
    svc: MatchingService = Depends(get_matching_svc),
):
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


@router.get("/runs")
def list_simulation_runs(
    db: Session = Depends(get_db),
):
    repo = AssignmentRepository(db)
    runs = repo.list_recent_runs(limit=20)
    return [
        {
            "id": r.id,
            "created_at": r.created_at.isoformat() if r.created_at else None,
            "algorithm": r.algorithm,
            "split": r.split,
            "cohort_size": r.cohort_size,
            "mean_compatibility": r.mean_compatibility,
            "quota_violations": r.quota_violations,
            "invalid_proposals": r.invalid_proposals,
            "gini_index": r.gini_index,
            "execution_time_ms": r.execution_time_ms,
        }
        for r in runs
    ]
