"""Pydantic schemas for Advisors and Faculty."""
from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class AdvisorBase(BaseModel):
    advisor_id: str
    advisor_name: str
    academic_title: str = ""
    primary_field: str = "Computer Science"
    email: Optional[str] = ""
    capacity: int = 5
    skill_count: int = 0
    publication_count: int = 0
    skills: List[str] = Field(default_factory=list)


class AdvisorRead(AdvisorBase):
    model_config = ConfigDict(from_attributes=True)


class AdvisorSkillEvidenceRead(BaseModel):
    skill: str
    skill_score: float
    evidence_count: int
    publication_evidence_count: int
    evidence_json: Optional[str] = "[]"

    model_config = ConfigDict(from_attributes=True)


class AdvisorDetail(AdvisorRead):
    department: str
    canonical_name: str
    profile_url: Optional[str] = None
    all_skills: List[AdvisorSkillEvidenceRead] = Field(default_factory=list)
    theses_supervised_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class LecturerRead(BaseModel):
    advisor_id: str
    canonical_name: str
    academic_title: str
    name: str
    profile_url: Optional[str] = None
    email: Optional[str] = None
    department: str

    model_config = ConfigDict(from_attributes=True)
