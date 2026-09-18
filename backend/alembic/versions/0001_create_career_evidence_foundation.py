"""Create the Career Evidence Foundation tables."""

from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "0001_career_evidence"
down_revision = None
branch_labels = None
depends_on = None


def uuid_column(nullable: bool = False) -> sa.Column:
    return sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=nullable)


def upgrade() -> None:
    op.create_table(
        "career_profiles",
        uuid_column(),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("display_name", sa.String(length=255), nullable=False),
    )
    op.create_index("ix_career_profiles_user_id", "career_profiles", ["user_id"], unique=False)

    op.create_table(
        "skills",
        uuid_column(),
        sa.Column("career_profile_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.ForeignKeyConstraint(["career_profile_id"], ["career_profiles.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("career_profile_id", "name", name="uq_skills_profile_name"),
    )
    op.create_index("ix_skills_career_profile_id", "skills", ["career_profile_id"], unique=False)

    op.create_table(
        "projects",
        uuid_column(),
        sa.Column("career_profile_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("url", sa.String(length=2048), nullable=True),
        sa.ForeignKeyConstraint(["career_profile_id"], ["career_profiles.id"], ondelete="CASCADE"),
    )
    op.create_index(
        "ix_projects_career_profile_id", "projects", ["career_profile_id"], unique=False
    )

    op.create_table(
        "experiences",
        uuid_column(),
        sa.Column("career_profile_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("organization", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("start_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("end_date", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["career_profile_id"], ["career_profiles.id"], ondelete="CASCADE"),
    )
    op.create_index(
        "ix_experiences_career_profile_id", "experiences", ["career_profile_id"], unique=False
    )

    op.create_table(
        "educations",
        uuid_column(),
        sa.Column("career_profile_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("institution", sa.String(length=255), nullable=False),
        sa.Column("field_of_study", sa.String(length=255), nullable=True),
        sa.Column("degree", sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(["career_profile_id"], ["career_profiles.id"], ondelete="CASCADE"),
    )
    op.create_index(
        "ix_educations_career_profile_id", "educations", ["career_profile_id"], unique=False
    )

    op.create_table(
        "certifications",
        uuid_column(),
        sa.Column("career_profile_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("issuer", sa.String(length=255), nullable=True),
        sa.Column("issued_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["career_profile_id"], ["career_profiles.id"], ondelete="CASCADE"),
    )
    op.create_index(
        "ix_certifications_career_profile_id", "certifications", ["career_profile_id"], unique=False
    )

    op.create_table(
        "evidence_sources",
        uuid_column(),
        sa.Column("source_type", sa.String(length=32), nullable=False),
        sa.Column("label", sa.String(length=255), nullable=False),
        sa.Column("uri", sa.String(length=2048), nullable=True),
        sa.Column("raw_content_ref", sa.String(length=2048), nullable=True),
        sa.Column("retrieved_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("source_type", "uri", name="uq_evidence_sources_type_uri"),
    )

    op.create_table(
        "evidence",
        uuid_column(),
        sa.Column("subject_type", sa.String(length=32), nullable=False),
        sa.Column("subject_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("evidence_source_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("excerpt", sa.Text(), nullable=True),
        sa.Column("relevance_note", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["evidence_source_id"], ["evidence_sources.id"], ondelete="CASCADE"
        ),
    )
    op.create_index("ix_evidence_subject", "evidence", ["subject_type", "subject_id"], unique=False)
    op.create_index(
        "ix_evidence_evidence_source_id", "evidence", ["evidence_source_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index("ix_evidence_evidence_source_id", table_name="evidence")
    op.drop_index("ix_evidence_subject", table_name="evidence")
    op.drop_table("evidence")
    op.drop_table("evidence_sources")
    op.drop_index("ix_certifications_career_profile_id", table_name="certifications")
    op.drop_table("certifications")
    op.drop_index("ix_educations_career_profile_id", table_name="educations")
    op.drop_table("educations")
    op.drop_index("ix_experiences_career_profile_id", table_name="experiences")
    op.drop_table("experiences")
    op.drop_index("ix_projects_career_profile_id", table_name="projects")
    op.drop_table("projects")
    op.drop_index("ix_skills_career_profile_id", table_name="skills")
    op.drop_table("skills")
    op.drop_index("ix_career_profiles_user_id", table_name="career_profiles")
    op.drop_table("career_profiles")
