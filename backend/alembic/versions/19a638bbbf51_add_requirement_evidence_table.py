"""Add requirement_evidence table."""

from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "19a638bbbf51"
down_revision = "d4810170b337"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "requirement_evidence",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("job_requirement_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "evidence_ids",
            postgresql.ARRAY(postgresql.UUID(as_uuid=True)),
            nullable=False,
        ),
        sa.Column("assessment", sa.String(length=32), nullable=False),
        sa.Column("explanation", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(
            ["job_requirement_id"], ["job_requirements.id"], ondelete="CASCADE"
        ),
        sa.UniqueConstraint(
            "job_requirement_id", name="uq_requirement_evidence_job_requirement_id"
        ),
    )


def downgrade() -> None:
    op.drop_table("requirement_evidence")
