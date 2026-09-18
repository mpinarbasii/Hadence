"""FastAPI dependency wiring for the infrastructure repositories."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.domain.ports.repositories import (
    CareerProfileRepository,
    CertificationRepository,
    EducationRepository,
    EvidenceRepository,
    EvidenceSourceRepository,
    ExperienceRepository,
    ProjectRepository,
    SkillRepository,
)
from app.infrastructure.db.engine import get_session
from app.infrastructure.db.repositories import (
    SqlAlchemyCareerProfileRepository,
    SqlAlchemyCertificationRepository,
    SqlAlchemyEducationRepository,
    SqlAlchemyEvidenceRepository,
    SqlAlchemyEvidenceSourceRepository,
    SqlAlchemyExperienceRepository,
    SqlAlchemyProjectRepository,
    SqlAlchemySkillRepository,
)


@dataclass(frozen=True)
class RepositoryBundle:
    profile: CareerProfileRepository
    skill: SkillRepository
    project: ProjectRepository
    experience: ExperienceRepository
    education: EducationRepository
    certification: CertificationRepository
    source: EvidenceSourceRepository
    evidence: EvidenceRepository


def get_repository_bundle() -> Iterator[RepositoryBundle]:
    session_iter = get_session()
    session: Session = next(session_iter)
    try:
        yield RepositoryBundle(
            profile=SqlAlchemyCareerProfileRepository(session),
            skill=SqlAlchemySkillRepository(session),
            project=SqlAlchemyProjectRepository(session),
            experience=SqlAlchemyExperienceRepository(session),
            education=SqlAlchemyEducationRepository(session),
            certification=SqlAlchemyCertificationRepository(session),
            source=SqlAlchemyEvidenceSourceRepository(session),
            evidence=SqlAlchemyEvidenceRepository(session),
        )
    finally:
        try:
            next(session_iter)
        except StopIteration:
            pass
