"""SQLAlchemy models for Faculty, Advisors, and Skill Evidences."""
from __future__ import annotations

from typing import List, Optional
from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.base import Base, TimestampMixin


class Advisor(Base, TimestampMixin):
    __tablename__ = "advisors"

    advisor_id: Mapped[str] = mapped_column(String(100), primary_key=True, index=True)
    source_ordinal: Mapped[int] = mapped_column(Integer, nullable=False, default=0, index=True)
    canonical_name: Mapped[str] = mapped_column(String(200), nullable=False)
    academic_title: Mapped[str] = mapped_column(String(50), nullable=False, default="")
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    profile_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(150), nullable=True, index=True)
    department: Mapped[str] = mapped_column(String(200), nullable=False)
    advisor_name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    primary_field: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    skill_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    skill_count: Mapped[int] = mapped_column(Integer, default=0)
    publication_evidence_count: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships
    skills: Mapped[List["AdvisorSkillEvidence"]] = relationship(
        "AdvisorSkillEvidence", back_populates="advisor", cascade="all, delete-orphan"
    )
    theses: Mapped[List["Thesis"]] = relationship("Thesis", back_populates="advisor")
    aliases: Mapped[List["AdvisorIdentityMap"]] = relationship(
        "AdvisorIdentityMap", back_populates="advisor", cascade="all, delete-orphan"
    )


class Lecturer(Base, TimestampMixin):
    __tablename__ = "lecturers"

    advisor_id: Mapped[str] = mapped_column(String(100), primary_key=True, index=True)
    canonical_name: Mapped[str] = mapped_column(String(200), nullable=False)
    academic_title: Mapped[str] = mapped_column(String(50), nullable=False, default="")
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    profile_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    department: Mapped[str] = mapped_column(String(200), nullable=False)


class AdvisorSkillEvidence(Base):
    __tablename__ = "advisor_skill_evidences"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    advisor_id: Mapped[str] = mapped_column(
        String(100), ForeignKey("advisors.advisor_id", ondelete="CASCADE"), index=True
    )
    canonical_name: Mapped[str] = mapped_column(String(200), nullable=False)
    skill: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    skill_score: Mapped[float] = mapped_column(Float, default=0.0)
    publication_evidence_count: Mapped[int] = mapped_column(Integer, default=0)
    evidence_count: Mapped[int] = mapped_column(Integer, default=0)
    evidence_json: Mapped[str] = mapped_column(Text, default="[]")

    advisor: Mapped["Advisor"] = relationship("Advisor", back_populates="skills")


class AdvisorIdentityMap(Base):
    __tablename__ = "advisor_identity_maps"

    source_name: Mapped[str] = mapped_column(String(200), primary_key=True)
    advisor_id: Mapped[str] = mapped_column(
        String(100), ForeignKey("advisors.advisor_id", ondelete="CASCADE"), index=True
    )
    canonical_name: Mapped[str] = mapped_column(String(200), nullable=False)
    match_method: Mapped[str] = mapped_column(String(50), nullable=False)
    match_score: Mapped[float] = mapped_column(Float, default=1.0)

    advisor: Mapped["Advisor"] = relationship("Advisor", back_populates="aliases")
