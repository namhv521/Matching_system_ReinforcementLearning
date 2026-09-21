"""Repository for Curriculum Courses."""
from __future__ import annotations

from typing import List, Optional
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from backend.app.models.course import Course


class CourseRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_courses(
        self,
        major_name: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Course]:
        stmt = select(Course)
        if major_name:
            stmt = stmt.where(Course.major_name == major_name)
        if search:
            pattern = f"%{search}%"
            stmt = stmt.where(
                or_(
                    Course.course_name.ilike(pattern),
                    Course.course_code.ilike(pattern),
                    Course.major_name.ilike(pattern),
                )
            )
        stmt = stmt.order_by(Course.major_name, Course.course_code).offset(offset).limit(limit)
        return list(self.db.scalars(stmt).all())

    def count_courses(
        self,
        major_name: Optional[str] = None,
        search: Optional[str] = None,
    ) -> int:
        stmt = select(func.count(Course.id))
        if major_name:
            stmt = stmt.where(Course.major_name == major_name)
        if search:
            pattern = f"%{search}%"
            stmt = stmt.where(
                or_(
                    Course.course_name.ilike(pattern),
                    Course.course_code.ilike(pattern),
                    Course.major_name.ilike(pattern),
                )
            )
        return self.db.scalar(stmt) or 0

    def upsert_course(self, data: dict) -> Course:
        stmt = select(Course).where(
            Course.course_code == data["course_code"],
            Course.major_name == data["major_name"],
        )
        obj = self.db.scalars(stmt).first()
        if obj:
            for k, v in data.items():
                setattr(obj, k, v)
        else:
            obj = Course(**data)
            self.db.add(obj)
        return obj
