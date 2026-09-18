"""In-memory repositories used by fast unit/API tests."""

from __future__ import annotations

from uuid import UUID

from app.domain.entities import CareerProfile, Evidence, EvidenceSource, Skill
from app.domain.value_objects import EvidenceSourceType


class InMemoryCareerProfileRepository:
    def __init__(self) -> None:
        self._by_id: dict[UUID, CareerProfile] = {}

    def save(self, profile: CareerProfile) -> None:
        self._by_id[profile.id] = profile

    def get(self, profile_id: UUID) -> CareerProfile | None:
        return self._by_id.get(profile_id)

    def get_by_user(self, user_id: UUID) -> CareerProfile | None:
        for profile in self._by_id.values():
            if profile.user_id == user_id:
                return profile
        return None


class InMemorySkillRepository:
    def __init__(self) -> None:
        self._by_id: dict[UUID, Skill] = {}

    def save(self, skill: Skill) -> None:
        self._by_id[skill.id] = skill

    def get(self, skill_id: UUID) -> Skill | None:
        return self._by_id.get(skill_id)

    def list_for_profile(self, career_profile_id: UUID) -> list[Skill]:
        return [s for s in self._by_id.values() if s.career_profile_id == career_profile_id]


class InMemoryEvidenceSourceRepository:
    def __init__(self) -> None:
        self._by_id: dict[UUID, EvidenceSource] = {}

    def save(self, source: EvidenceSource) -> None:
        self._by_id[source.id] = source

    def get(self, source_id: UUID) -> EvidenceSource | None:
        return self._by_id.get(source_id)

    def get_by_uri(self, source_type: EvidenceSourceType, uri: str) -> EvidenceSource | None:
        for source in self._by_id.values():
            if source.source_type == source_type and source.uri == uri:
                return source
        return None


class InMemoryEvidenceRepository:
    def __init__(self) -> None:
        self._items: list[Evidence] = []

    def save(self, evidence: Evidence) -> None:
        self._items.append(evidence)

    def list_for_subject(self, subject_type: str, subject_id: UUID) -> list[Evidence]:
        return [
            e for e in self._items if e.subject_type == subject_type and e.subject_id == subject_id
        ]
