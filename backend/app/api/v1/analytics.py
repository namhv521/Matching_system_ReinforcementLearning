"""Analytics endpoints for API v1."""
from typing import Any, Dict, List
from fastapi import APIRouter, Depends

from backend.app.api.dependencies import get_analytics_svc
from backend.app.schemas.analytics import (
    BenchmarkItem,
    FigureItem,
    OverviewResponse,
    TrainingCurvesResponse,
)
from backend.app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Decision Support Analytics"])


@router.get("/overview", response_model=OverviewResponse)
def get_overview(svc: AnalyticsService = Depends(get_analytics_svc)):
    return svc.get_overview()


@router.get("/benchmarks", response_model=List[BenchmarkItem])
def get_benchmarks(svc: AnalyticsService = Depends(get_analytics_svc)):
    return svc.get_benchmarks()


@router.get("/training-curves", response_model=TrainingCurvesResponse)
def get_training_curves(svc: AnalyticsService = Depends(get_analytics_svc)):
    return svc.get_training_curves()


@router.get("/figures", response_model=List[FigureItem])
def get_figures(svc: AnalyticsService = Depends(get_analytics_svc)):
    return svc.get_figures_list()
