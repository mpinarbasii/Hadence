"""In-memory repositories used by fast unit/API tests."""

from __future__ import annotations

from uuid import UUID

from app.domain.entities import (
    CareerProfile,
    Certification,
    Education,
    Evidence,
    EvidenceSource,
    Experience,
    Job,
    JobRequirement,
    Project,
    RequirementEvidence,
    Skill,
)
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


class InMemoryProjectRepository:
    def __init__(self) -> None:
        self._by_id: dict[UUID, Project] = {}

    def save(self, project: Project) -> None:
        self._by_id[project.id] = project

    def get(self, project_id: UUID) -> Project | None:
        return self._by_id.get(project_id)

    def list_for_profile(self, career_profile_id: UUID) -> list[Project]:
        return [p for p in self._by_id.values() if p.career_profile_id == career_profile_id]


class InMemoryExperienceRepository:
    def __init__(self) -> None:
        self._by_id: dict[UUID, Experience] = {}

    def save(self, experience: Experience) -> None:
        self._by_id[experience.id] = experience

    def get(self, experience_id: UUID) -> Experience | None:
        return self._by_id.get(experience_id)

    def list_for_profile(self, career_profile_id: UUID) -> list[Experience]:
        return [e for e in self._by_id.values() if e.career_profile_id == career_profile_id]


class InMemoryEducationRepository:
    def __init__(self) -> None:
        self._by_id: dict[UUID, Education] = {}

    def save(self, education: Education) -> None:
        self._by_id[education.id] = education

    def get(self, education_id: UUID) -> Education | None:
        return self._by_id.get(education_id)

    def list_for_profile(self, career_profile_id: UUID) -> list[Education]:
        return [e for e in self._by_id.values() if e.career_profile_id == career_profile_id]


class InMemoryCertificationRepository:
    def __init__(self) -> None:
        self._by_id: dict[UUID, Certification] = {}

    def save(self, certification: Certification) -> None:
        self._by_id[certification.id] = certification

    def get(self, certification_id: UUID) -> Certification | None:
        return self._by_id.get(certification_id)

    def list_for_profile(self, career_profile_id: UUID) -> list[Certification]:
        return [c for c in self._by_id.values() if c.career_profile_id == career_profile_id]


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


class InMemoryJobRepository:
    def __init__(self) -> None:
        self._by_id: dict[UUID, Job] = {}

    def save(self, job: Job) -> None:
        self._by_id[job.id] = job

    def get(self, job_id: UUID) -> Job | None:
        return self._by_id.get(job_id)


class InMemoryJobRequirementRepository:
    def __init__(self) -> None:
        self._items: list[JobRequirement] = []

    def save(self, requirement: JobRequirement) -> None:
        self._items.append(requirement)

    def list_for_job(self, job_id: UUID) -> list[JobRequirement]:
        return [r for r in self._items if r.job_id == job_id]


class InMemoryRequirementEvidenceRepository:
    def __init__(
        self, job_requirement_repo: InMemoryJobRequirementRepository | None = None
    ) -> None:
        self._by_requirement_id: dict[UUID, RequirementEvidence] = {}
        self._job_requirement_repo = job_requirement_repo

    def save(self, requirement_evidence: RequirementEvidence) -> None:
        self._by_requirement_id[requirement_evidence.job_requirement_id] = requirement_evidence

    def get_for_requirement(self, job_requirement_id: UUID) -> RequirementEvidence | None:
        return self._by_requirement_id.get(job_requirement_id)

    def list_for_job(self, job_id: UUID) -> list[RequirementEvidence]:
        if self._job_requirement_repo is None:
            return []
        job_requirement_ids = {r.id for r in self._job_requirement_repo.list_for_job(job_id)}
        return [
            re
            for re in self._by_requirement_id.values()
            if re.job_requirement_id in job_requirement_ids
        ]
