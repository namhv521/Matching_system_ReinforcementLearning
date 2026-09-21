"""Pydantic schemas for Curriculum Courses."""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class CourseRead(BaseModel):
    id: int
    major_name: str
    major_url: str
    course_name: str
    course_code: str
    credits: int

    model_config = ConfigDict(from_attributes=True)
