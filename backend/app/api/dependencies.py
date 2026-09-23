"""FastAPI dependency wiring for the infrastructure repositories."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.config import get_settings
from app.domain.ports.github_client import GitHubClient
from app.domain.ports.llm_provider import LLMProvider
from app.domain.ports.repositories import (
    CareerProfileRepository,
    CertificationRepository,
    EducationRepository,
    EvidenceRepository,
    EvidenceSourceRepository,
    ExperienceRepository,
    JobRepository,
    JobRequirementRepository,
    ProjectRepository,
    RequirementEvidenceRepository,
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
    SqlAlchemyJobRepository,
    SqlAlchemyJobRequirementRepository,
    SqlAlchemyProjectRepository,
    SqlAlchemyRequirementEvidenceRepository,
    SqlAlchemySkillRepository,
)
from app.infrastructure.integrations.github.client import HttpGitHubClient
from app.infrastructure.llm.anthropic_provider import AnthropicLLMProvider


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
    job: JobRepository
    job_requirement: JobRequirementRepository
    requirement_evidence: RequirementEvidenceRepository


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
            job=SqlAlchemyJobRepository(session),
            job_requirement=SqlAlchemyJobRequirementRepository(session),
            requirement_evidence=SqlAlchemyRequirementEvidenceRepository(session),
        )
    finally:
        try:
            next(session_iter)
        except StopIteration:
            pass


def get_github_client() -> GitHubClient:
    return HttpGitHubClient(token=get_settings().github_token)


def get_llm_provider() -> LLMProvider:
    api_key = get_settings().anthropic_api_key
    if not api_key:
        raise RuntimeError(
            "ANTHROPIC_API_KEY is not set — required for job requirement extraction. "
            "Set it in your .env file."
        )
    return AnthropicLLMProvider(api_key=api_key)
