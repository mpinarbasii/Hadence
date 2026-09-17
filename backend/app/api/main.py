"""FastAPI entrypoint.

NOTE: repositories are wired as process-local in-memory singletons for now.
This is intentional for the Phase 1 foundation slice — real Postgres-backed
repositories land in the next slice (see docs/architecture.md §8) and will
be swapped in here via FastAPI's dependency-injection system without any
change to app/domain or app/application.
"""

from __future__ import annotations

from uuid import UUID

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.application.use_cases import add_skill, attach_evidence_to_skill, create_career_profile
from app.domain.value_objects import EvidenceSourceType
from app.infrastructure.db.in_memory import (
    InMemoryCareerProfileRepository,
    InMemoryEvidenceRepository,
    InMemoryEvidenceSourceRepository,
    InMemorySkillRepository,
)

app = FastAPI(title="Hadence API", version="0.1.0")

# Process-local singletons — see module docstring.
_profile_repo = InMemoryCareerProfileRepository()
_skill_repo = InMemorySkillRepository()
_source_repo = InMemoryEvidenceSourceRepository()
_evidence_repo = InMemoryEvidenceRepository()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


class CreateProfileRequest(BaseModel):
    user_id: UUID
    display_name: str


class ProfileResponse(BaseModel):
    id: UUID
    user_id: UUID
    display_name: str
    skill_ids: list[UUID]


@app.post("/profiles", response_model=ProfileResponse)
def create_profile(payload: CreateProfileRequest) -> ProfileResponse:
    profile = create_career_profile(
        repo=_profile_repo, user_id=payload.user_id, display_name=payload.display_name
    )
    return ProfileResponse(**profile.__dict__)


@app.get("/profiles/{profile_id}", response_model=ProfileResponse)
def get_profile(profile_id: UUID) -> ProfileResponse:
    profile = _profile_repo.get(profile_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    return ProfileResponse(**profile.__dict__)


class AddSkillRequest(BaseModel):
    name: str


class SkillResponse(BaseModel):
    id: UUID
    career_profile_id: UUID
    name: str


@app.post("/profiles/{profile_id}/skills", response_model=SkillResponse)
def create_skill(profile_id: UUID, payload: AddSkillRequest) -> SkillResponse:
    try:
        skill = add_skill(
            profile_repo=_profile_repo,
            skill_repo=_skill_repo,
            career_profile_id=profile_id,
            name=payload.name,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return SkillResponse(**skill.__dict__)


class AttachEvidenceRequest(BaseModel):
    source_type: EvidenceSourceType
    source_label: str
    source_uri: str | None = None
    excerpt: str | None = None
    relevance_note: str | None = None


class EvidenceResponse(BaseModel):
    id: UUID
    subject_type: str
    subject_id: UUID
    evidence_source_id: UUID
    excerpt: str | None
    relevance_note: str | None


@app.post("/skills/{skill_id}/evidence", response_model=EvidenceResponse)
def create_evidence(skill_id: UUID, payload: AttachEvidenceRequest) -> EvidenceResponse:
    try:
        evidence = attach_evidence_to_skill(
            skill_repo=_skill_repo,
            source_repo=_source_repo,
            evidence_repo=_evidence_repo,
            skill_id=skill_id,
            source_type=payload.source_type,
            source_label=payload.source_label,
            source_uri=payload.source_uri,
            excerpt=payload.excerpt,
            relevance_note=payload.relevance_note,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return EvidenceResponse(
        id=evidence.id,
        subject_type=evidence.subject_type.value,
        subject_id=evidence.subject_id,
        evidence_source_id=evidence.evidence_source_id,
        excerpt=evidence.excerpt,
        relevance_note=evidence.relevance_note,
    )
