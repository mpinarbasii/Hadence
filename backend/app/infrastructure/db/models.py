"""SQLAlchemy persistence models for the Career Evidence Foundation."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class CareerProfileModel(Base):
    __tablename__ = "career_profiles"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False, index=True)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)

    skills: Mapped[list[SkillModel]] = relationship(
        back_populates="profile", cascade="all, delete-orphan"
    )
    projects: Mapped[list[ProjectModel]] = relationship(
        back_populates="profile", cascade="all, delete-orphan"
    )
    experiences: Mapped[list[ExperienceModel]] = relationship(
        back_populates="profile", cascade="all, delete-orphan"
    )
    educations: Mapped[list[EducationModel]] = relationship(
        back_populates="profile", cascade="all, delete-orphan"
    )
    certifications: Mapped[list[CertificationModel]] = relationship(
        back_populates="profile", cascade="all, delete-orphan"
    )


class SkillModel(Base):
    __tablename__ = "skills"
    __table_args__ = (UniqueConstraint("career_profile_id", "name", name="uq_skills_profile_name"),)

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    career_profile_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("career_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    profile: Mapped[CareerProfileModel] = relationship(back_populates="skills")


class ProjectModel(Base):
    __tablename__ = "projects"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    career_profile_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("career_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    url: Mapped[str | None] = mapped_column(String(2048), nullable=True)

    profile: Mapped[CareerProfileModel] = relationship(back_populates="projects")


class ExperienceModel(Base):
    __tablename__ = "experiences"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    career_profile_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("career_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    organization: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    start_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    end_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    profile: Mapped[CareerProfileModel] = relationship(back_populates="experiences")


class EducationModel(Base):
    __tablename__ = "educations"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    career_profile_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("career_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    institution: Mapped[str] = mapped_column(String(255), nullable=False)
    field_of_study: Mapped[str | None] = mapped_column(String(255), nullable=True)
    degree: Mapped[str | None] = mapped_column(String(255), nullable=True)

    profile: Mapped[CareerProfileModel] = relationship(back_populates="educations")


class CertificationModel(Base):
    __tablename__ = "certifications"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    career_profile_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("career_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    issuer: Mapped[str | None] = mapped_column(String(255), nullable=True)
    issued_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    profile: Mapped[CareerProfileModel] = relationship(back_populates="certifications")


class EvidenceSourceModel(Base):
    __tablename__ = "evidence_sources"
    __table_args__ = (UniqueConstraint("source_type", "uri", name="uq_evidence_sources_type_uri"),)

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    source_type: Mapped[str] = mapped_column(String(32), nullable=False)
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    uri: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    raw_content_ref: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    retrieved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    last_verified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    evidence_records: Mapped[list[EvidenceModel]] = relationship(
        back_populates="source", cascade="all, delete-orphan"
    )


class EvidenceModel(Base):
    __tablename__ = "evidence"
    __table_args__ = (Index("ix_evidence_subject", "subject_type", "subject_id"),)

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    subject_type: Mapped[str] = mapped_column(String(32), nullable=False)
    subject_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    evidence_source_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("evidence_sources.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    excerpt: Mapped[str | None] = mapped_column(Text, nullable=True)
    relevance_note: Mapped[str | None] = mapped_column(Text, nullable=True)

    source: Mapped[EvidenceSourceModel] = relationship(back_populates="evidence_records")


class JobModel(Base):
    """See app/domain/entities.py:Job — raw_description is preserved
    verbatim and never edited; JobRequirementModel rows stay traceable
    back to it via source_quote."""

    __tablename__ = "jobs"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    company: Mapped[str] = mapped_column(String(255), nullable=False)
    raw_description: Mapped[str] = mapped_column(Text, nullable=False)
    source_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    requirements: Mapped[list[JobRequirementModel]] = relationship(
        back_populates="job", cascade="all, delete-orphan"
    )


class JobRequirementModel(Base):
    __tablename__ = "job_requirements"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    job_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    text: Mapped[str] = mapped_column(String(500), nullable=False)
    requirement_type: Mapped[str] = mapped_column(String(32), nullable=False)
    source_quote: Mapped[str] = mapped_column(Text, nullable=False)

    job: Mapped[JobModel] = relationship(back_populates="requirements")


class RequirementEvidenceModel(Base):
    """See app/domain/entities.py:RequirementEvidence — recomputable
    mapping, one row per job_requirement_id (unique constraint below
    enforces the upsert-by-requirement semantics the repository relies
    on)."""

    __tablename__ = "requirement_evidence"
    __table_args__ = (
        UniqueConstraint("job_requirement_id", name="uq_requirement_evidence_job_requirement_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    job_requirement_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("job_requirements.id", ondelete="CASCADE"),
        nullable=False,
    )
    evidence_ids: Mapped[list[uuid.UUID]] = mapped_column(
        ARRAY(PG_UUID(as_uuid=True)), nullable=False
    )
    assessment: Mapped[str] = mapped_column(String(32), nullable=False)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
