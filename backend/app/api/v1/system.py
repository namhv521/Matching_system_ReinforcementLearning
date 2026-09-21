"""System health and audit endpoints for API v1."""
from typing import Any, Dict
from fastapi import APIRouter, Depends

from backend.app.api.dependencies import get_analytics_svc
from backend.app.schemas.analytics import QualityReportResponse, SystemHealthResponse
from backend.app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/system", tags=["System Health & Diagnostics"])


@router.get("/health", response_model=SystemHealthResponse)
def get_health(svc: AnalyticsService = Depends(get_analytics_svc)):
    return svc.get_system_health()


@router.get("/quality-report")
def get_quality_report(svc: AnalyticsService = Depends(get_analytics_svc)) -> Dict[str, Any]:
    return svc.get_quality_report()


@router.get("/mongodb-status")
def get_mongodb_status() -> Dict[str, Any]:
    from backend.app.core.config import settings
    from backend.app.db.mongodb import ping_mongodb

    ping = ping_mongodb()
    return {
        "enabled": settings.MONGODB_ENABLED,
        "database_name": settings.MONGODB_DB_NAME,
        "connection": ping,
    }
