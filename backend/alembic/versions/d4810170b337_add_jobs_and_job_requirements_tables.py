"""Add jobs and job_requirements tables."""

from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "d4810170b337"
down_revision = "0001_career_evidence"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("company", sa.String(length=255), nullable=False),
        sa.Column("raw_description", sa.Text(), nullable=False),
        sa.Column("source_url", sa.String(length=2048), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "job_requirements",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("job_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("text", sa.String(length=500), nullable=False),
        sa.Column("requirement_type", sa.String(length=32), nullable=False),
        sa.Column("source_quote", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_job_requirements_job_id", "job_requirements", ["job_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_job_requirements_job_id", table_name="job_requirements")
    op.drop_table("job_requirements")
    op.drop_table("jobs")
