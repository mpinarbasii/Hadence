"""Core domain entities for the Hadence Career Evidence Foundation.

The domain layer is framework-independent: no FastAPI, Pydantic, SQLAlchemy,
or LLM SDK imports are allowed here.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID, uuid4

from app.domain.value_objects import EvidenceSourceType, EvidenceSubjectType


@dataclass
class EvidenceSource:
    """Stable, reusable provenance record.

    The source identity can be reused by multiple evidence records. Metadata
    such as last_verified_at may evolve over time; individual Evidence rows
    preserve the subject-specific explanation of why the source is relevant.
    """

    id: UUID
    source_type: EvidenceSourceType
    label: str
    retrieved_at: datetime
    uri: str | None = None
    raw_content_ref: str | None = None
    last_verified_at: datetime | None = None

    @staticmethod
    def create(
        source_type: EvidenceSourceType,
        label: str,
        uri: str | None = None,
        raw_content_ref: str | None = None,
    ) -> EvidenceSource:
        return EvidenceSource(
            id=uuid4(),
            source_type=source_type,
            label=label,
            uri=uri,
            raw_content_ref=raw_content_ref,
            retrieved_at=datetime.now(UTC),
        )


@dataclass(frozen=True)
class Evidence:
    """Subject-specific link between a career object and a source."""

    id: UUID
    subject_type: EvidenceSubjectType
    subject_id: UUID
    evidence_source_id: UUID
    excerpt: str | None = None
    relevance_note: str | None = None

    @staticmethod
    def create(
        subject_type: EvidenceSubjectType,
        subject_id: UUID,
        evidence_source_id: UUID,
        excerpt: str | None = None,
        relevance_note: str | None = None,
    ) -> Evidence:
        return Evidence(
            id=uuid4(),
            subject_type=subject_type,
            subject_id=subject_id,
            evidence_source_id=evidence_source_id,
            excerpt=excerpt,
            relevance_note=relevance_note,
        )


@dataclass
class Skill:
    id: UUID
    career_profile_id: UUID
    name: str

    @staticmethod
    def create(career_profile_id: UUID, name: str) -> Skill:
        return Skill(id=uuid4(), career_profile_id=career_profile_id, name=name)


@dataclass
class Project:
    id: UUID
    career_profile_id: UUID
    name: str
    description: str | None = None
    url: str | None = None

    @staticmethod
    def create(
        career_profile_id: UUID,
        name: str,
        description: str | None = None,
        url: str | None = None,
    ) -> Project:
        return Project(
            id=uuid4(),
            career_profile_id=career_profile_id,
            name=name,
            description=description,
            url=url,
        )


@dataclass
class Experience:
    id: UUID
    career_profile_id: UUID
    title: str
    organization: str
    description: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None

    @staticmethod
    def create(
        career_profile_id: UUID,
        title: str,
        organization: str,
        description: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> Experience:
        return Experience(
            id=uuid4(),
            career_profile_id=career_profile_id,
            title=title,
            organization=organization,
            description=description,
            start_date=start_date,
            end_date=end_date,
        )


@dataclass
class Education:
    id: UUID
    career_profile_id: UUID
    institution: str
    field_of_study: str | None = None
    degree: str | None = None

    @staticmethod
    def create(
        career_profile_id: UUID,
        institution: str,
        field_of_study: str | None = None,
        degree: str | None = None,
    ) -> Education:
        return Education(
            id=uuid4(),
            career_profile_id=career_profile_id,
            institution=institution,
            field_of_study=field_of_study,
            degree=degree,
        )


@dataclass
class Certification:
    id: UUID
    career_profile_id: UUID
    name: str
    issuer: str | None = None
    issued_at: datetime | None = None

    @staticmethod
    def create(
        career_profile_id: UUID,
        name: str,
        issuer: str | None = None,
        issued_at: datetime | None = None,
    ) -> Certification:
        return Certification(
            id=uuid4(),
            career_profile_id=career_profile_id,
            name=name,
            issuer=issuer,
            issued_at=issued_at,
        )


@dataclass
class CareerProfile:
    """Minimal aggregate root for the user's career evidence graph."""

    id: UUID
    user_id: UUID
    display_name: str
    skill_ids: list[UUID] = field(default_factory=list)
    project_ids: list[UUID] = field(default_factory=list)
    experience_ids: list[UUID] = field(default_factory=list)
    education_ids: list[UUID] = field(default_factory=list)
    certification_ids: list[UUID] = field(default_factory=list)

    @staticmethod
    def create(user_id: UUID, display_name: str) -> CareerProfile:
        return CareerProfile(id=uuid4(), user_id=user_id, display_name=display_name)

    def _add_unique(self, collection: list[UUID], entity_id: UUID, label: str) -> None:
        if entity_id in collection:
            raise ValueError(f"{label} {entity_id} is already linked to this profile")
        collection.append(entity_id)

    def add_skill(self, skill_id: UUID) -> None:
        self._add_unique(self.skill_ids, skill_id, "Skill")

    def add_project(self, project_id: UUID) -> None:
        self._add_unique(self.project_ids, project_id, "Project")

    def add_experience(self, experience_id: UUID) -> None:
        self._add_unique(self.experience_ids, experience_id, "Experience")

    def add_education(self, education_id: UUID) -> None:
        self._add_unique(self.education_ids, education_id, "Education")

    def add_certification(self, certification_id: UUID) -> None:
        self._add_unique(self.certification_ids, certification_id, "Certification")
