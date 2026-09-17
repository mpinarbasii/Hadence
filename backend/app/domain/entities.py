"""Core domain entities for the Career Evidence Foundation (Phase 1).

Kept intentionally minimal: Job / JobRequirement / RequirementEvidence /
Application entities are added in later phases (see docs/domain-model.md),
once Job Intelligence and Evidence Mapping are implemented. Adding them here
before there's a use case for them would be speculative.

Pure dataclasses on purpose: no ORM/Pydantic coupling in the domain layer.
Validation belongs to the API schemas (api/) and construction logic below;
persistence mapping belongs to infrastructure/db/.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID, uuid4

from app.domain.value_objects import EvidenceSourceType, EvidenceSubjectType


@dataclass
class EvidenceSource:
    """A stable, reusable provenance record — not an immutable aggregate root.

    The same logical source (e.g. one GitHub repository, one uploaded CV) is
    represented by a single `EvidenceSource` and its identity is reused
    across every `Evidence` record that points back to it — see
    docs/domain-model.md §2 and the Step 3 evidence-source/evidence
    separation. Metadata such as `last_verified_at` may change over time
    (re-verification updates it in place); this is not treated as creating a
    new provenance identity.

    `Evidence` records are what carry the subject-specific, explainable
    context (excerpt, relevance_note) — `EvidenceSource` itself only needs to
    answer "where did this come from" and "when was it last checked".
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

    def mark_verified(self) -> None:
        """Record that this source was re-checked, without changing its identity."""
        self.last_verified_at = datetime.now(UTC)


@dataclass(frozen=True)
class Evidence:
    """Join entity linking a profile item to the source that supports it.

    Not an independent concept — see docs/domain-model.md §1. Always has
    exactly one subject and one source.
    """

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
    """Aggregate root for a user's evidence graph.

    Mutation of the profile's child-id collections (skills, projects, ...)
    must go through the `add_*` methods below rather than touching the
    lists directly, so id-uniqueness stays an enforced invariant instead of
    a convention callers have to remember.

    The aggregate boundary here is intentionally minimal: it only owns
    id-references to its children, not the child entities themselves, and
    the only invariant enforced today is "no duplicate child id". This is a
    deliberate choice to avoid over-engineering DDD aggregate boundaries
    before there's a concrete persistence/consistency requirement driving
    them. The boundary may need to evolve once PostgreSQL persistence and
    cross-entity workflows (e.g. deleting a skill that has evidence
    attached) are introduced — see docs/architecture.md.
    """

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

    def add_skill(self, skill_id: UUID) -> None:
        _append_unique(self.skill_ids, skill_id)

    def add_project(self, project_id: UUID) -> None:
        _append_unique(self.project_ids, project_id)

    def add_experience(self, experience_id: UUID) -> None:
        _append_unique(self.experience_ids, experience_id)

    def add_education(self, education_id: UUID) -> None:
        _append_unique(self.education_ids, education_id)

    def add_certification(self, certification_id: UUID) -> None:
        _append_unique(self.certification_ids, certification_id)


def _append_unique(ids: list[UUID], new_id: UUID) -> None:
    if new_id in ids:
        raise ValueError(f"Duplicate id {new_id} — already present on this profile")
    ids.append(new_id)
