"""FastAPI dependency wiring for the infrastructure repositories."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.domain.ports.repositories import (
    CareerProfileRepository,
    EvidenceRepository,
    EvidenceSourceRepository,
    SkillRepository,
)
from app.infrastructure.db.engine import get_session
from app.infrastructure.db.repositories import (
    SqlAlchemyCareerProfileRepository,
    SqlAlchemyEvidenceRepository,
    SqlAlchemyEvidenceSourceRepository,
    SqlAlchemySkillRepository,
)


@dataclass(frozen=True)
class RepositoryBundle:
    profile: CareerProfileRepository
    skill: SkillRepository
    source: EvidenceSourceRepository
    evidence: EvidenceRepository


def get_repository_bundle() -> Iterator[RepositoryBundle]:
    session_iter = get_session()
    session: Session = next(session_iter)
    try:
        yield RepositoryBundle(
            profile=SqlAlchemyCareerProfileRepository(session),
            skill=SqlAlchemySkillRepository(session),
            source=SqlAlchemyEvidenceSourceRepository(session),
            evidence=SqlAlchemyEvidenceRepository(session),
        )
    finally:
        try:
            next(session_iter)
        except StopIteration:
            pass
