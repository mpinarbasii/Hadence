"""FastAPI entrypoint for Hadence."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.api.dependencies import RepositoryBundle, get_repository_bundle
from app.application.use_cases import (
    add_certification,
    add_education,
    add_experience,
    add_project,
    add_skill,
    attach_evidence_to_skill,
    create_career_profile,
)
from app.config import get_settings
from app.domain.value_objects import EvidenceSourceType

app = FastAPI(title="Hadence API", version="0.1.0")

_settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        origin.strip() for origin in _settings.api_cors_origins.split(",") if origin.strip()
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
    project_ids: list[UUID]
    experience_ids: list[UUID]
    education_ids: list[UUID]
    certification_ids: list[UUID]


@app.post("/profiles", response_model=ProfileResponse)
def create_profile(
    payload: CreateProfileRequest,
    repos: RepositoryBundle = Depends(get_repository_bundle),
) -> ProfileResponse:
    profile = create_career_profile(
        repo=repos.profile,
        user_id=payload.user_id,
        display_name=payload.display_name,
    )
    return ProfileResponse(
        id=profile.id,
        user_id=profile.user_id,
        display_name=profile.display_name,
        skill_ids=profile.skill_ids,
        project_ids=profile.project_ids,
        experience_ids=profile.experience_ids,
        education_ids=profile.education_ids,
        certification_ids=profile.certification_ids,
    )


@app.get("/profiles/{profile_id}", response_model=ProfileResponse)
def get_profile(
    profile_id: UUID,
    repos: RepositoryBundle = Depends(get_repository_bundle),
) -> ProfileResponse:
    profile = repos.profile.get(profile_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    return ProfileResponse(
        id=profile.id,
        user_id=profile.user_id,
        display_name=profile.display_name,
        skill_ids=profile.skill_ids,
        project_ids=profile.project_ids,
        experience_ids=profile.experience_ids,
        education_ids=profile.education_ids,
        certification_ids=profile.certification_ids,
    )


class AddSkillRequest(BaseModel):
    name: str


class SkillResponse(BaseModel):
    id: UUID
    career_profile_id: UUID
    name: str


@app.post("/profiles/{profile_id}/skills", response_model=SkillResponse)
def create_skill(
    profile_id: UUID,
    payload: AddSkillRequest,
    repos: RepositoryBundle = Depends(get_repository_bundle),
) -> SkillResponse:
    try:
        skill = add_skill(
            profile_repo=repos.profile,
            skill_repo=repos.skill,
            career_profile_id=profile_id,
            name=payload.name,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return SkillResponse(id=skill.id, career_profile_id=skill.career_profile_id, name=skill.name)


class AddProjectRequest(BaseModel):
    name: str
    description: str | None = None
    url: str | None = None


class ProjectResponse(BaseModel):
    id: UUID
    career_profile_id: UUID
    name: str
    description: str | None
    url: str | None


@app.post("/profiles/{profile_id}/projects", response_model=ProjectResponse)
def create_project(
    profile_id: UUID,
    payload: AddProjectRequest,
    repos: RepositoryBundle = Depends(get_repository_bundle),
) -> ProjectResponse:
    try:
        project = add_project(
            profile_repo=repos.profile,
            project_repo=repos.project,
            career_profile_id=profile_id,
            name=payload.name,
            description=payload.description,
            url=payload.url,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return ProjectResponse(
        id=project.id,
        career_profile_id=project.career_profile_id,
        name=project.name,
        description=project.description,
        url=project.url,
    )


class AddExperienceRequest(BaseModel):
    title: str
    organization: str
    description: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None


class ExperienceResponse(BaseModel):
    id: UUID
    career_profile_id: UUID
    title: str
    organization: str
    description: str | None
    start_date: datetime | None
    end_date: datetime | None


@app.post("/profiles/{profile_id}/experiences", response_model=ExperienceResponse)
def create_experience(
    profile_id: UUID,
    payload: AddExperienceRequest,
    repos: RepositoryBundle = Depends(get_repository_bundle),
) -> ExperienceResponse:
    try:
        experience = add_experience(
            profile_repo=repos.profile,
            experience_repo=repos.experience,
            career_profile_id=profile_id,
            title=payload.title,
            organization=payload.organization,
            description=payload.description,
            start_date=payload.start_date,
            end_date=payload.end_date,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return ExperienceResponse(
        id=experience.id,
        career_profile_id=experience.career_profile_id,
        title=experience.title,
        organization=experience.organization,
        description=experience.description,
        start_date=experience.start_date,
        end_date=experience.end_date,
    )


class AddEducationRequest(BaseModel):
    institution: str
    field_of_study: str | None = None
    degree: str | None = None


class EducationResponse(BaseModel):
    id: UUID
    career_profile_id: UUID
    institution: str
    field_of_study: str | None
    degree: str | None


@app.post("/profiles/{profile_id}/educations", response_model=EducationResponse)
def create_education(
    profile_id: UUID,
    payload: AddEducationRequest,
    repos: RepositoryBundle = Depends(get_repository_bundle),
) -> EducationResponse:
    try:
        education = add_education(
            profile_repo=repos.profile,
            education_repo=repos.education,
            career_profile_id=profile_id,
            institution=payload.institution,
            field_of_study=payload.field_of_study,
            degree=payload.degree,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return EducationResponse(
        id=education.id,
        career_profile_id=education.career_profile_id,
        institution=education.institution,
        field_of_study=education.field_of_study,
        degree=education.degree,
    )


class AddCertificationRequest(BaseModel):
    name: str
    issuer: str | None = None
    issued_at: datetime | None = None


class CertificationResponse(BaseModel):
    id: UUID
    career_profile_id: UUID
    name: str
    issuer: str | None
    issued_at: datetime | None


@app.post("/profiles/{profile_id}/certifications", response_model=CertificationResponse)
def create_certification(
    profile_id: UUID,
    payload: AddCertificationRequest,
    repos: RepositoryBundle = Depends(get_repository_bundle),
) -> CertificationResponse:
    try:
        certification = add_certification(
            profile_repo=repos.profile,
            certification_repo=repos.certification,
            career_profile_id=profile_id,
            name=payload.name,
            issuer=payload.issuer,
            issued_at=payload.issued_at,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return CertificationResponse(
        id=certification.id,
        career_profile_id=certification.career_profile_id,
        name=certification.name,
        issuer=certification.issuer,
        issued_at=certification.issued_at,
    )


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
def create_evidence(
    skill_id: UUID,
    payload: AttachEvidenceRequest,
    repos: RepositoryBundle = Depends(get_repository_bundle),
) -> EvidenceResponse:
    try:
        evidence = attach_evidence_to_skill(
            skill_repo=repos.skill,
            source_repo=repos.source,
            evidence_repo=repos.evidence,
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
