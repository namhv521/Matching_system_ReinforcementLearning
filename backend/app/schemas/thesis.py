"""Pydantic schemas for Theses and Student Profiles."""
from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class ThesisBase(BaseModel):
    student_id: str
    student_name: str
    thesis_title: str
    field_category: str
    completion_year: int
    advisor_name_historical: str
    tech_stack: List[str] = Field(default_factory=list)


class ThesisRead(ThesisBase):
    record_id: Optional[str] = None
    major: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ThesisDetail(ThesisRead):
    thesis_grade: Optional[float] = None
    web_languages: Optional[str] = None
    frontend_frameworks: Optional[str] = None
    backend_frameworks: Optional[str] = None
    database_cache: Optional[str] = None
    web_api_tech: Optional[str] = None
    ai_frameworks: Optional[str] = None
    ai_problems: Optional[str] = None
    game_engine: Optional[str] = None
    research_methods: Optional[str] = None
    research_output: Optional[str] = None
    source_file: Optional[str] = None
    primary_role: Optional[str] = None
    secondary_roles: Optional[str] = None
    advisor_id: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class StudentProfileRead(BaseModel):
    record_id: str
    student_id: Optional[str] = None
    student_name: Optional[str] = None
    primary_role: str
    secondary_roles: Optional[str] = None
    field_category: str

    model_config = ConfigDict(from_attributes=True)
