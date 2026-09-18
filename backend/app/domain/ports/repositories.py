"""Repository interfaces (ports) for the domain/application layers."""

from __future__ import annotations

from typing import Protocol
from uuid import UUID

from app.domain.entities import (
    CareerProfile,
    Certification,
    Education,
    Evidence,
    EvidenceSource,
    Experience,
    Project,
    Skill,
)
from app.domain.value_objects import EvidenceSourceType


class CareerProfileRepository(Protocol):
    def save(self, profile: CareerProfile) -> None: ...

    def get(self, profile_id: UUID) -> CareerProfile | None: ...

    def get_by_user(self, user_id: UUID) -> CareerProfile | None: ...


class SkillRepository(Protocol):
    def save(self, skill: Skill) -> None: ...

    def get(self, skill_id: UUID) -> Skill | None: ...

    def list_for_profile(self, career_profile_id: UUID) -> list[Skill]: ...


class ProjectRepository(Protocol):
    def save(self, project: Project) -> None: ...

    def get(self, project_id: UUID) -> Project | None: ...

    def list_for_profile(self, career_profile_id: UUID) -> list[Project]: ...


class ExperienceRepository(Protocol):
    def save(self, experience: Experience) -> None: ...

    def get(self, experience_id: UUID) -> Experience | None: ...

    def list_for_profile(self, career_profile_id: UUID) -> list[Experience]: ...


class EducationRepository(Protocol):
    def save(self, education: Education) -> None: ...

    def get(self, education_id: UUID) -> Education | None: ...

    def list_for_profile(self, career_profile_id: UUID) -> list[Education]: ...


class CertificationRepository(Protocol):
    def save(self, certification: Certification) -> None: ...

    def get(self, certification_id: UUID) -> Certification | None: ...

    def list_for_profile(self, career_profile_id: UUID) -> list[Certification]: ...


class EvidenceSourceRepository(Protocol):
    def save(self, source: EvidenceSource) -> None: ...

    def get(self, source_id: UUID) -> EvidenceSource | None: ...

    def get_by_uri(self, source_type: EvidenceSourceType, uri: str) -> EvidenceSource | None: ...


class EvidenceRepository(Protocol):
    def save(self, evidence: Evidence) -> None: ...

    def list_for_subject(self, subject_type: str, subject_id: UUID) -> list[Evidence]: ...
