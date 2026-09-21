"""Advisor and Faculty domain service."""
from __future__ import annotations

from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from backend.app.core.exceptions import EntityNotFoundError
from backend.app.repositories.advisor_repository import AdvisorRepository
from backend.app.schemas.advisor import AdvisorDetail, AdvisorRead, AdvisorSkillEvidenceRead
from backend.app.schemas.common import PageMeta, PaginatedResponse


class AdvisorService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = AdvisorRepository(db)

    def list_advisors(
        self,
        department: Optional[str] = None,
        primary_field: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> PaginatedResponse[AdvisorRead]:
        offset = (page - 1) * page_size
        items = self.repo.list_advisors(
            department=department,
            primary_field=primary_field,
            search=search,
            limit=page_size,
            offset=offset,
        )
        total = self.repo.count_advisors(department=department, primary_field=primary_field, search=search)

        records: List[AdvisorRead] = []
        for adv in items:
            skills = (adv.skill_text or "").split()[:8]
            records.append(
                AdvisorRead(
                    advisor_id=adv.advisor_id,
                    advisor_name=adv.advisor_name,
                    academic_title=adv.academic_title,
                    primary_field=adv.primary_field,
                    email=adv.email or "",
                    capacity=5,  # default balanced capacity
                    skill_count=adv.skill_count,
                    publication_count=adv.publication_evidence_count,
                    skills=skills,
                )
            )

        meta = PageMeta.create(page=page, page_size=page_size, total=total)
        return PaginatedResponse(data=records, meta=meta)

    def get_advisor_detail(self, advisor_id: str) -> AdvisorDetail:
        adv = self.repo.get_by_id(advisor_id)
        if not adv:
            raise EntityNotFoundError("Advisor", advisor_id)

        skill_evidences = [
            AdvisorSkillEvidenceRead(
                skill=s.skill,
                skill_score=s.skill_score,
                evidence_count=s.evidence_count,
                publication_evidence_count=s.publication_evidence_count,
                evidence_json=s.evidence_json,
            )
            for s in adv.skills
        ]

        skills_summary = (adv.skill_text or "").split()[:10]
        return AdvisorDetail(
            advisor_id=adv.advisor_id,
            advisor_name=adv.advisor_name,
            canonical_name=adv.canonical_name,
            academic_title=adv.academic_title,
            primary_field=adv.primary_field,
            department=adv.department,
            profile_url=adv.profile_url,
            email=adv.email or "",
            capacity=5,
            skill_count=adv.skill_count,
            publication_count=adv.publication_evidence_count,
            skills=skills_summary,
            all_skills=skill_evidences,
            theses_supervised_count=len(adv.theses),
        )
