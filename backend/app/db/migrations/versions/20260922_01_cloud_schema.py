"""create Supabase cloud schema

Revision ID: 20260922_01
Revises: 520930ca106d
Create Date: 2026-09-22
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260922_01"
down_revision: Union[str, None] = "520930ca106d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


class Vector(sa.types.UserDefinedType):
    """Dimensionless pgvector column reserved for a later embedding benchmark."""

    def get_col_spec(self, **_: object) -> str:
        return "vector"


def _timestamps() -> tuple[sa.Column, sa.Column]:
    return (
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "advisors",
        sa.Column("advisor_id", sa.String(length=100), primary_key=True),
        sa.Column("canonical_name", sa.String(length=200), nullable=False),
        sa.Column("academic_title", sa.String(length=50), nullable=False, server_default=""),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("profile_url", sa.String(length=500)),
        sa.Column("email", sa.String(length=150)),
        sa.Column("department", sa.String(length=200), nullable=False),
        sa.Column("advisor_name", sa.String(length=200), nullable=False),
        sa.Column("primary_field", sa.String(length=100), nullable=False),
        sa.Column("skill_text", sa.Text()),
        sa.Column("skill_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("publication_evidence_count", sa.Integer(), nullable=False, server_default="0"),
        *_timestamps(),
    )
    op.create_index("ix_advisors_email", "advisors", ["email"])
    op.create_index("ix_advisors_advisor_name", "advisors", ["advisor_name"])
    op.create_index("ix_advisors_primary_field", "advisors", ["primary_field"])

    op.create_table(
        "lecturers",
        sa.Column("advisor_id", sa.String(length=100), primary_key=True),
        sa.Column("canonical_name", sa.String(length=200), nullable=False),
        sa.Column("academic_title", sa.String(length=50), nullable=False, server_default=""),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("profile_url", sa.String(length=500)),
        sa.Column("email", sa.String(length=150)),
        sa.Column("department", sa.String(length=200), nullable=False),
        *_timestamps(),
    )

    op.create_table(
        "advisor_skill_evidences",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("advisor_id", sa.String(length=100), sa.ForeignKey("advisors.advisor_id", ondelete="CASCADE"), nullable=False),
        sa.Column("canonical_name", sa.String(length=200), nullable=False),
        sa.Column("skill", sa.String(length=100), nullable=False),
        sa.Column("skill_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("publication_evidence_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("evidence_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("evidence_json", sa.Text(), nullable=False, server_default="[]"),
        sa.UniqueConstraint("advisor_id", "skill", name="uq_advisor_skill_evidence"),
    )
    op.create_index("ix_advisor_skill_evidences_advisor_id", "advisor_skill_evidences", ["advisor_id"])
    op.create_index("ix_advisor_skill_evidences_skill", "advisor_skill_evidences", ["skill"])

    op.create_table(
        "advisor_identity_maps",
        sa.Column("source_name", sa.String(length=200), primary_key=True),
        sa.Column("advisor_id", sa.String(length=100), sa.ForeignKey("advisors.advisor_id", ondelete="CASCADE"), nullable=False),
        sa.Column("canonical_name", sa.String(length=200), nullable=False),
        sa.Column("match_method", sa.String(length=50), nullable=False),
        sa.Column("match_score", sa.Float(), nullable=False, server_default="1"),
    )
    op.create_index("ix_advisor_identity_maps_advisor_id", "advisor_identity_maps", ["advisor_id"])

    op.create_table(
        "theses",
        sa.Column("record_id", sa.String(length=100), primary_key=True),
        sa.Column("student_id", sa.String(length=50)),
        sa.Column("student_name", sa.String(length=150)),
        sa.Column("major", sa.String(length=150), nullable=False),
        sa.Column("completion_year", sa.Integer(), nullable=False, server_default="2025"),
        sa.Column("thesis_title", sa.Text(), nullable=False),
        sa.Column("field_category", sa.String(length=100), nullable=False),
        sa.Column("advisor_name", sa.String(length=200), nullable=False),
        sa.Column("thesis_grade", sa.Float()),
        sa.Column("web_languages", sa.String(length=255)),
        sa.Column("frontend_frameworks", sa.String(length=255)),
        sa.Column("backend_frameworks", sa.String(length=255)),
        sa.Column("database_cache", sa.String(length=255)),
        sa.Column("web_api_tech", sa.String(length=255)),
        sa.Column("app_languages", sa.String(length=255)),
        sa.Column("app_frameworks", sa.String(length=255)),
        sa.Column("app_db_backend", sa.String(length=255)),
        sa.Column("mobile_client_tech", sa.String(length=255)),
        sa.Column("architecture", sa.String(length=255)),
        sa.Column("ai_frameworks", sa.String(length=255)),
        sa.Column("ai_problems", sa.String(length=255)),
        sa.Column("data_tools", sa.String(length=255)),
        sa.Column("data_models", sa.String(length=255)),
        sa.Column("game_engine", sa.String(length=255)),
        sa.Column("game_type", sa.String(length=255)),
        sa.Column("specialty_field", sa.String(length=255)),
        sa.Column("tools_environment", sa.String(length=255)),
        sa.Column("hardware", sa.String(length=255)),
        sa.Column("iot_protocol", sa.String(length=255)),
        sa.Column("research_methods", sa.String(length=255)),
        sa.Column("research_output", sa.String(length=255)),
        sa.Column("source_file", sa.String(length=300), nullable=False, unique=True),
        sa.Column("extraction_status", sa.String(length=50), nullable=False, server_default="success"),
        sa.Column("advisor_name_raw", sa.String(length=200), nullable=False),
        sa.Column("advisor_id", sa.String(length=100), sa.ForeignKey("advisors.advisor_id", ondelete="SET NULL")),
        sa.Column("advisor_match_method", sa.String(length=50), nullable=False, server_default="exact_normalized"),
        sa.Column("advisor_match_score", sa.Float(), nullable=False, server_default="1"),
        sa.Column("primary_role", sa.String(length=100), nullable=False),
        sa.Column("secondary_roles", sa.String(length=255)),
        sa.Column("search_embedding", Vector(), nullable=True),
        *_timestamps(),
    )
    for name, column in (
        ("ix_theses_student_id", "student_id"),
        ("ix_theses_major", "major"),
        ("ix_theses_completion_year", "completion_year"),
        ("ix_theses_field_category", "field_category"),
        ("ix_theses_advisor_id", "advisor_id"),
        ("ix_theses_primary_role", "primary_role"),
    ):
        op.create_index(name, "theses", [column])

    op.create_table(
        "student_profiles",
        sa.Column("record_id", sa.String(length=100), sa.ForeignKey("theses.record_id", ondelete="CASCADE"), primary_key=True),
        sa.Column("student_id", sa.String(length=50)),
        sa.Column("student_name", sa.String(length=150)),
        sa.Column("primary_role", sa.String(length=100), nullable=False),
        sa.Column("secondary_roles", sa.String(length=255)),
        sa.Column("field_category", sa.String(length=100), nullable=False),
        *_timestamps(),
    )
    op.create_index("ix_student_profiles_student_id", "student_profiles", ["student_id"])
    op.create_index("ix_student_profiles_primary_role", "student_profiles", ["primary_role"])
    op.create_index("ix_student_profiles_field_category", "student_profiles", ["field_category"])

    op.create_table(
        "courses",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("major_name", sa.String(length=150), nullable=False),
        sa.Column("major_url", sa.String(length=500), nullable=False),
        sa.Column("table_index", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("course_name", sa.String(length=200), nullable=False),
        sa.Column("course_code", sa.String(length=50), nullable=False),
        sa.Column("credits", sa.Integer(), nullable=False, server_default="3"),
        sa.Column("raw_cells", sa.Text(), nullable=False, server_default="[]"),
        sa.UniqueConstraint("major_name", "course_code", name="uq_course_major_code"),
        *_timestamps(),
    )
    op.create_index("ix_courses_major_name", "courses", ["major_name"])
    op.create_index("ix_courses_course_name", "courses", ["course_name"])
    op.create_index("ix_courses_course_code", "courses", ["course_code"])

    op.create_table(
        "benchmark_metrics",
        sa.Column("algorithm", sa.String(length=50), primary_key=True),
        sa.Column("total_reward", sa.Float()),
        sa.Column("mean_compatibility", sa.Float(), nullable=False),
        sa.Column("constraint_violations", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("quota_violations", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("invalid_proposals", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("gini_index", sa.Float(), nullable=False, server_default="0"),
        sa.Column("execution_time_ms", sa.Float(), nullable=False, server_default="0"),
        sa.Column("accuracy_vs_historical", sa.Float()),
        *_timestamps(),
    )

    op.create_table(
        "training_curve_points",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("algorithm", sa.String(length=50), nullable=False),
        sa.Column("milestone", sa.Integer(), nullable=False),
        sa.Column("train_reward", sa.Float(), nullable=False),
        sa.Column("val_reward", sa.Float(), nullable=False),
        sa.Column("train_compatibility", sa.Float(), nullable=False),
        sa.Column("val_compatibility", sa.Float(), nullable=False),
        sa.Column("invalid_proposals", sa.Integer(), nullable=False, server_default="0"),
        sa.UniqueConstraint("algorithm", "milestone", name="uq_training_curve_algorithm_milestone"),
        *_timestamps(),
    )
    op.create_index("ix_training_curve_points_algorithm", "training_curve_points", ["algorithm"])

    op.create_table(
        "cohort_runs",
        sa.Column("id", sa.String(length=50), primary_key=True),
        sa.Column("algorithm", sa.String(length=50), nullable=False),
        sa.Column("split", sa.String(length=20), nullable=False),
        sa.Column("cohort_size", sa.Integer(), nullable=False),
        sa.Column("mean_compatibility", sa.Float(), nullable=False),
        sa.Column("quota_violations", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("invalid_proposals", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("gini_index", sa.Float(), nullable=False, server_default="0"),
        sa.Column("execution_time_ms", sa.Float(), nullable=False, server_default="0"),
        sa.Column("total_reward", sa.Float()),
        sa.Column("accuracy_vs_historical", sa.Float()),
        *_timestamps(),
    )
    op.create_index("ix_cohort_runs_algorithm", "cohort_runs", ["algorithm"])
    op.create_index("ix_cohort_runs_split", "cohort_runs", ["split"])

    op.create_table(
        "assignment_records",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("cohort_run_id", sa.String(length=50), sa.ForeignKey("cohort_runs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("step", sa.Integer(), nullable=False),
        sa.Column("student_id", sa.String(length=50), nullable=False),
        sa.Column("student_name", sa.String(length=150), nullable=False),
        sa.Column("thesis_title", sa.String(length=500), nullable=False),
        sa.Column("field_category", sa.String(length=100), nullable=False),
        sa.Column("assigned_advisor_id", sa.String(length=100), nullable=False),
        sa.Column("assigned_advisor_name", sa.String(length=200), nullable=False),
        sa.Column("academic_title", sa.String(length=50), nullable=False, server_default=""),
        sa.Column("compatibility_score", sa.Float(), nullable=False),
        sa.Column("historical_advisor", sa.String(length=200), nullable=False, server_default=""),
        sa.Column("historical_match", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.create_index("ix_assignment_records_cohort_run_id", "assignment_records", ["cohort_run_id"])

    op.create_table(
        "advisor_workload_records",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("cohort_run_id", sa.String(length=50), sa.ForeignKey("cohort_runs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("advisor_name", sa.String(length=200), nullable=False),
        sa.Column("capacity", sa.Integer(), nullable=False),
        sa.Column("assigned", sa.Integer(), nullable=False),
        sa.Column("remaining", sa.Integer(), nullable=False),
        sa.Column("utilization_pct", sa.Float(), nullable=False, server_default="0"),
    )
    op.create_index("ix_advisor_workload_records_cohort_run_id", "advisor_workload_records", ["cohort_run_id"])


def downgrade() -> None:
    for table in (
        "advisor_workload_records",
        "assignment_records",
        "cohort_runs",
        "training_curve_points",
        "benchmark_metrics",
        "courses",
        "student_profiles",
        "theses",
        "advisor_identity_maps",
        "advisor_skill_evidences",
        "lecturers",
        "advisors",
    ):
        op.drop_table(table)
    # Keep pgvector installed: it may be shared by later migrations or user data.
