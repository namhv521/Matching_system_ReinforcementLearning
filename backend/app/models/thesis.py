"""SQLAlchemy models for Theses and Student Profiles."""
from __future__ import annotations

from typing import Optional
from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.base import Base, TimestampMixin


class Thesis(Base, TimestampMixin):
    __tablename__ = "theses"

    record_id: Mapped[str] = mapped_column(String(100), primary_key=True, index=True)
    source_ordinal: Mapped[int] = mapped_column(Integer, nullable=False, default=0, index=True)
    student_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    student_name: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    major: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    completion_year: Mapped[int] = mapped_column(Integer, nullable=False, default=2025, index=True)
    thesis_title: Mapped[str] = mapped_column(Text, nullable=False)
    field_category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    advisor_name: Mapped[str] = mapped_column(String(200), nullable=False)
    thesis_grade: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Technical Stack extraction fields
    web_languages: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    frontend_frameworks: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    backend_frameworks: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    database_cache: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    web_api_tech: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    app_languages: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    app_frameworks: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    app_db_backend: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    mobile_client_tech: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    architecture: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    ai_frameworks: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    ai_problems: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    data_tools: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    data_models: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    game_engine: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    game_type: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    specialty_field: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    tools_environment: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    hardware: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    iot_protocol: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    research_methods: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    research_output: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Ingestion provenance
    source_file: Mapped[str] = mapped_column(String(300), unique=True, nullable=False)
    extraction_status: Mapped[str] = mapped_column(String(50), default="success")
    advisor_name_raw: Mapped[str] = mapped_column(String(200), nullable=False)
    advisor_id: Mapped[Optional[str]] = mapped_column(
        String(100), ForeignKey("advisors.advisor_id", ondelete="SET NULL"), nullable=True, index=True
    )
    advisor_match_method: Mapped[str] = mapped_column(String(50), default="exact_normalized")
    advisor_match_score: Mapped[float] = mapped_column(Float, default=1.0)
    primary_role: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    secondary_roles: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Relationships
    advisor: Mapped[Optional["Advisor"]] = relationship("Advisor", back_populates="theses")
    student_profile: Mapped[Optional["StudentProfile"]] = relationship(
        "StudentProfile", back_populates="thesis", uselist=False, cascade="all, delete-orphan"
    )


class StudentProfile(Base, TimestampMixin):
    __tablename__ = "student_profiles"

    record_id: Mapped[str] = mapped_column(
        String(100), ForeignKey("theses.record_id", ondelete="CASCADE"), primary_key=True
    )
    student_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    student_name: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    primary_role: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    secondary_roles: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    field_category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    thesis: Mapped["Thesis"] = relationship("Thesis", back_populates="student_profile")
