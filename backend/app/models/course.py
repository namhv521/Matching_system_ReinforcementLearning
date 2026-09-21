"""SQLAlchemy model for Curriculum Courses."""
from __future__ import annotations

from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.base import Base, TimestampMixin


class Course(Base, TimestampMixin):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    major_name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    major_url: Mapped[str] = mapped_column(String(500), nullable=False)
    table_index: Mapped[int] = mapped_column(Integer, default=0)
    course_name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    course_code: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    credits: Mapped[int] = mapped_column(Integer, default=3)
    raw_cells: Mapped[str] = mapped_column(Text, default="[]")
