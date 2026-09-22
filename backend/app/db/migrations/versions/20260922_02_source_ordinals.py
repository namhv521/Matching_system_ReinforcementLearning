"""preserve public snapshot ordering for matching

Revision ID: 20260922_02
Revises: 20260922_01
Create Date: 2026-09-22
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260922_02"
down_revision: Union[str, None] = "20260922_01"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    for table in ("advisors", "theses"):
        op.add_column(table, sa.Column("source_ordinal", sa.Integer(), nullable=False, server_default="0"))
        op.create_index(f"ix_{table}_source_ordinal", table, ["source_ordinal"])


def downgrade() -> None:
    for table in ("theses", "advisors"):
        op.drop_index(f"ix_{table}_source_ordinal", table_name=table)
        op.drop_column(table, "source_ordinal")
