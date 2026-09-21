"""Advisors endpoints for API v1."""
from typing import Optional
from fastapi import APIRouter, Depends, Query

from backend.app.api.dependencies import get_advisor_svc
from backend.app.schemas.advisor import AdvisorDetail, AdvisorRead
from backend.app.schemas.common import PaginatedResponse
from backend.app.services.advisor_service import AdvisorService

router = APIRouter(prefix="/advisors", tags=["Advisors & Faculty Directory"])


@router.get("", response_model=PaginatedResponse[AdvisorRead])
def list_advisors(
    department: Optional[str] = Query(None, description="Filter by department"),
    primary_field: Optional[str] = Query(None, description="Filter by primary research field"),
    search: Optional[str] = Query(None, description="Search keyword in name or skills"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    svc: AdvisorService = Depends(get_advisor_svc),
):
    return svc.list_advisors(
        department=department,
        primary_field=primary_field,
        search=search,
        page=page,
        page_size=page_size,
    )


@router.get("/{advisor_id}", response_model=AdvisorDetail)
def get_advisor_detail(
    advisor_id: str,
    svc: AdvisorService = Depends(get_advisor_svc),
):
    return svc.get_advisor_detail(advisor_id)
