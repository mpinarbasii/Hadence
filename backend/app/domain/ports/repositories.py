"""Repository interfaces (ports) for the domain/application layers."""

from __future__ import annotations

from typing import Protocol
from uuid import UUID

from app.domain.entities import CareerProfile, Evidence, EvidenceSource, Skill
from app.domain.value_objects import EvidenceSourceType


class CareerProfileRepository(Protocol):
    def save(self, profile: CareerProfile) -> None: ...

    def get(self, profile_id: UUID) -> CareerProfile | None: ...

    def get_by_user(self, user_id: UUID) -> CareerProfile | None: ...


class SkillRepository(Protocol):
    def save(self, skill: Skill) -> None: ...

    def get(self, skill_id: UUID) -> Skill | None: ...

    def list_for_profile(self, career_profile_id: UUID) -> list[Skill]: ...


class EvidenceSourceRepository(Protocol):
    def save(self, source: EvidenceSource) -> None: ...

    def get(self, source_id: UUID) -> EvidenceSource | None: ...

    def get_by_uri(self, source_type: EvidenceSourceType, uri: str) -> EvidenceSource | None: ...


class EvidenceRepository(Protocol):
    def save(self, evidence: Evidence) -> None: ...

    def list_for_subject(self, subject_type: str, subject_id: UUID) -> list[Evidence]: ...
