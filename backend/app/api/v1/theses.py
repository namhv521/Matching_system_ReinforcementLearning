"""Theses catalog endpoints for API v1."""
from typing import Optional
from fastapi import APIRouter, Depends, Query

from backend.app.api.dependencies import get_thesis_svc
from backend.app.schemas.common import PaginatedResponse
from backend.app.schemas.thesis import ThesisDetail, ThesisRead
from backend.app.services.thesis_service import ThesisService

router = APIRouter(prefix="/theses", tags=["Theses Catalog"])


@router.get("", response_model=PaginatedResponse[ThesisRead])
def list_theses(
    major: Optional[str] = Query(None, description="Filter by major"),
    field_category: Optional[str] = Query(None, description="Filter by domain/category"),
    completion_year: Optional[int] = Query(None, description="Filter by completion year"),
    advisor_name: Optional[str] = Query(None, description="Filter by advisor name"),
    search: Optional[str] = Query(None, description="Search keyword in title, student name, or ID"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    svc: ThesisService = Depends(get_thesis_svc),
):
    return svc.list_theses(
        major=major,
        field_category=field_category,
        completion_year=completion_year,
        advisor_name=advisor_name,
        search=search,
        page=page,
        page_size=page_size,
    )


@router.get("/{record_id}", response_model=ThesisDetail)
def get_thesis_detail(
    record_id: str,
    svc: ThesisService = Depends(get_thesis_svc),
):
    return svc.get_thesis_detail(record_id)
