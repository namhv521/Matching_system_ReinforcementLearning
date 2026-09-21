"""Thesis and Student profile domain service."""
from __future__ import annotations

from typing import List, Optional
from sqlalchemy.orm import Session

from backend.app.core.exceptions import EntityNotFoundError
from backend.app.data.transformers.normalizers import extract_tech_stack
from backend.app.repositories.thesis_repository import ThesisRepository
from backend.app.schemas.common import PageMeta, PaginatedResponse
from backend.app.schemas.thesis import ThesisDetail, ThesisRead


class ThesisService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ThesisRepository(db)

    def list_theses(
        self,
        major: Optional[str] = None,
        field_category: Optional[str] = None,
        completion_year: Optional[int] = None,
        advisor_name: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> PaginatedResponse[ThesisRead]:
        offset = (page - 1) * page_size
        items = self.repo.list_theses(
            major=major,
            field_category=field_category,
            completion_year=completion_year,
            advisor_name=advisor_name,
            search=search,
            limit=page_size,
            offset=offset,
        )
        total = self.repo.count_theses(
            major=major,
            field_category=field_category,
            completion_year=completion_year,
            advisor_name=advisor_name,
            search=search,
        )

        records: List[ThesisRead] = []
        for t in items:
            stack = extract_tech_stack({
                "web_languages": t.web_languages,
                "backend_frameworks": t.backend_frameworks,
                "frontend_frameworks": t.frontend_frameworks,
                "ai_frameworks": t.ai_frameworks,
                "database_cache": t.database_cache,
            })
            records.append(
                ThesisRead(
                    record_id=t.record_id,
                    student_id=t.student_id or "",
                    student_name=t.student_name or "Sinh viên",
                    thesis_title=t.thesis_title,
                    field_category=t.field_category,
                    completion_year=t.completion_year,
                    advisor_name_historical=t.advisor_name,
                    major=t.major,
                    tech_stack=stack,
                )
            )

        meta = PageMeta.create(page=page, page_size=page_size, total=total)
        return PaginatedResponse(data=records, meta=meta)

    def get_thesis_detail(self, record_id: str) -> ThesisDetail:
        t = self.repo.get_by_record_id(record_id)
        if not t:
            raise EntityNotFoundError("Thesis", record_id)

        stack = extract_tech_stack({
            "web_languages": t.web_languages,
            "backend_frameworks": t.backend_frameworks,
            "frontend_frameworks": t.frontend_frameworks,
            "ai_frameworks": t.ai_frameworks,
            "database_cache": t.database_cache,
        })
        return ThesisDetail(
            record_id=t.record_id,
            student_id=t.student_id or "",
            student_name=t.student_name or "Sinh viên",
            thesis_title=t.thesis_title,
            field_category=t.field_category,
            completion_year=t.completion_year,
            advisor_name_historical=t.advisor_name,
            major=t.major,
            tech_stack=stack,
            thesis_grade=t.thesis_grade,
            web_languages=t.web_languages,
            frontend_frameworks=t.frontend_frameworks,
            backend_frameworks=t.backend_frameworks,
            database_cache=t.database_cache,
            web_api_tech=t.web_api_tech,
            ai_frameworks=t.ai_frameworks,
            ai_problems=t.ai_problems,
            game_engine=t.game_engine,
            research_methods=t.research_methods,
            research_output=t.research_output,
            source_file=t.source_file,
            primary_role=t.primary_role,
            secondary_roles=t.secondary_roles,
            advisor_id=t.advisor_id,
        )
