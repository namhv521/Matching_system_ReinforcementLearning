"""Repository for Thesis and Student Profile database operations."""
from __future__ import annotations

from typing import List, Optional
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from backend.app.models.thesis import Thesis, StudentProfile


class ThesisRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_record_id(self, record_id: str) -> Optional[Thesis]:
        stmt = (
            select(Thesis)
            .where(Thesis.record_id == record_id)
            .options(
                selectinload(Thesis.student_profile),
                selectinload(Thesis.advisor),
            )
        )
        return self.db.scalars(stmt).first()

    def get_by_student_id(self, student_id: str) -> Optional[Thesis]:
        stmt = select(Thesis).where(Thesis.student_id == student_id)
        return self.db.scalars(stmt).first()

    def list_for_matching(self) -> List[Thesis]:
        stmt = select(Thesis).order_by(Thesis.source_ordinal, Thesis.record_id)
        return list(self.db.scalars(stmt).all())

    def list_theses(
        self,
        major: Optional[str] = None,
        field_category: Optional[str] = None,
        completion_year: Optional[int] = None,
        advisor_name: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Thesis]:
        stmt = select(Thesis)
        if major:
            stmt = stmt.where(Thesis.major == major)
        if field_category:
            stmt = stmt.where(Thesis.field_category == field_category)
        if completion_year:
            stmt = stmt.where(Thesis.completion_year == completion_year)
        if advisor_name:
            stmt = stmt.where(Thesis.advisor_name == advisor_name)
        if search:
            pattern = f"%{search}%"
            stmt = stmt.where(
                or_(
                    Thesis.thesis_title.ilike(pattern),
                    Thesis.student_name.ilike(pattern),
                    Thesis.student_id.ilike(pattern),
                    Thesis.field_category.ilike(pattern),
                    Thesis.advisor_name.ilike(pattern),
                )
            )
        stmt = stmt.order_by(Thesis.completion_year.desc(), Thesis.record_id).offset(offset).limit(limit)
        return list(self.db.scalars(stmt).all())

    def count_theses(
        self,
        major: Optional[str] = None,
        field_category: Optional[str] = None,
        completion_year: Optional[int] = None,
        advisor_name: Optional[str] = None,
        search: Optional[str] = None,
    ) -> int:
        stmt = select(func.count(Thesis.record_id))
        if major:
            stmt = stmt.where(Thesis.major == major)
        if field_category:
            stmt = stmt.where(Thesis.field_category == field_category)
        if completion_year:
            stmt = stmt.where(Thesis.completion_year == completion_year)
        if advisor_name:
            stmt = stmt.where(Thesis.advisor_name == advisor_name)
        if search:
            pattern = f"%{search}%"
            stmt = stmt.where(
                or_(
                    Thesis.thesis_title.ilike(pattern),
                    Thesis.student_name.ilike(pattern),
                    Thesis.student_id.ilike(pattern),
                    Thesis.field_category.ilike(pattern),
                    Thesis.advisor_name.ilike(pattern),
                )
            )
        return self.db.scalar(stmt) or 0

    def upsert_thesis(self, data: dict) -> Thesis:
        obj = self.db.get(Thesis, data["record_id"])
        if obj:
            for k, v in data.items():
                setattr(obj, k, v)
        else:
            obj = Thesis(**data)
            self.db.add(obj)
        return obj

    def upsert_student_profile(self, data: dict) -> StudentProfile:
        obj = self.db.get(StudentProfile, data["record_id"])
        if obj:
            for k, v in data.items():
                setattr(obj, k, v)
        else:
            obj = StudentProfile(**data)
            self.db.add(obj)
        return obj
