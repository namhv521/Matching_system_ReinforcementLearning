"""Curriculum courses endpoints for API v1."""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.repositories.course_repository import CourseRepository
from backend.app.schemas.common import PageMeta, PaginatedResponse
from backend.app.schemas.course import CourseRead

router = APIRouter(prefix="/courses", tags=["Curriculum Courses"])


@router.get("", response_model=PaginatedResponse[CourseRead])
def list_courses(
    major_name: Optional[str] = Query(None, description="Filter by major curriculum"),
    search: Optional[str] = Query(None, description="Search course name or course code"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
):
    repo = CourseRepository(db)
    offset = (page - 1) * page_size
    items = repo.list_courses(major_name=major_name, search=search, limit=page_size, offset=offset)
    total = repo.count_courses(major_name=major_name, search=search)

    records = [
        CourseRead(
            id=c.id,
            major_name=c.major_name,
            major_url=c.major_url,
            course_name=c.course_name,
            course_code=c.course_code,
            credits=c.credits,
        )
        for c in items
    ]
    meta = PageMeta.create(page=page, page_size=page_size, total=total)
    return PaginatedResponse(data=records, meta=meta)
