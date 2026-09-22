"""Repository for Advisor, Lecturer, and Skill Evidence persistence."""
from __future__ import annotations

from typing import List, Optional
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from backend.app.models.advisor import (
    Advisor,
    Lecturer,
    AdvisorSkillEvidence,
    AdvisorIdentityMap,
)


class AdvisorRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, advisor_id: str) -> Optional[Advisor]:
        stmt = (
            select(Advisor)
            .where(Advisor.advisor_id == advisor_id)
            .options(
                selectinload(Advisor.skills),
                selectinload(Advisor.theses),
            )
        )
        return self.db.scalars(stmt).first()

    def get_by_name(self, advisor_name: str) -> Optional[Advisor]:
        stmt = select(Advisor).where(Advisor.advisor_name == advisor_name)
        return self.db.scalars(stmt).first()

    def list_for_matching(self) -> List[Advisor]:
        stmt = select(Advisor).order_by(Advisor.created_at, Advisor.advisor_id)
        return list(self.db.scalars(stmt).all())

    def list_advisors(
        self,
        department: Optional[str] = None,
        primary_field: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Advisor]:
        stmt = select(Advisor)
        if department:
            stmt = stmt.where(Advisor.department == department)
        if primary_field:
            stmt = stmt.where(Advisor.primary_field == primary_field)
        if search:
            pattern = f"%{search}%"
            stmt = stmt.where(
                or_(
                    Advisor.advisor_name.ilike(pattern),
                    Advisor.name.ilike(pattern),
                    Advisor.primary_field.ilike(pattern),
                    Advisor.skill_text.ilike(pattern),
                )
            )
        stmt = stmt.order_by(Advisor.advisor_name).offset(offset).limit(limit)
        return list(self.db.scalars(stmt).all())

    def count_advisors(
        self,
        department: Optional[str] = None,
        primary_field: Optional[str] = None,
        search: Optional[str] = None,
    ) -> int:
        stmt = select(func.count(Advisor.advisor_id))
        if department:
            stmt = stmt.where(Advisor.department == department)
        if primary_field:
            stmt = stmt.where(Advisor.primary_field == primary_field)
        if search:
            pattern = f"%{search}%"
            stmt = stmt.where(
                or_(
                    Advisor.advisor_name.ilike(pattern),
                    Advisor.name.ilike(pattern),
                    Advisor.primary_field.ilike(pattern),
                    Advisor.skill_text.ilike(pattern),
                )
            )
        return self.db.scalar(stmt) or 0

    def upsert_advisor(self, data: dict) -> Advisor:
        obj = self.db.get(Advisor, data["advisor_id"])
        if obj:
            for k, v in data.items():
                setattr(obj, k, v)
        else:
            obj = Advisor(**data)
            self.db.add(obj)
        return obj

    def upsert_lecturer(self, data: dict) -> Lecturer:
        obj = self.db.get(Lecturer, data["advisor_id"])
        if obj:
            for k, v in data.items():
                setattr(obj, k, v)
        else:
            obj = Lecturer(**data)
            self.db.add(obj)
        return obj

    def upsert_skill_evidence(self, data: dict) -> AdvisorSkillEvidence:
        stmt = select(AdvisorSkillEvidence).where(
            AdvisorSkillEvidence.advisor_id == data["advisor_id"],
            AdvisorSkillEvidence.skill == data["skill"],
        )
        obj = self.db.scalars(stmt).first()
        if obj:
            for k, v in data.items():
                setattr(obj, k, v)
        else:
            obj = AdvisorSkillEvidence(**data)
            self.db.add(obj)
        return obj

    def upsert_identity_map(self, data: dict) -> AdvisorIdentityMap:
        obj = self.db.get(AdvisorIdentityMap, data["source_name"])
        if obj:
            for k, v in data.items():
                setattr(obj, k, v)
        else:
            obj = AdvisorIdentityMap(**data)
            self.db.add(obj)
        return obj
