"""Application-layer use cases for the Hadence Career Evidence Foundation."""

from __future__ import annotations

from datetime import datetime
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
from app.domain.value_objects import EvidenceSourceType, EvidenceSubjectType


def create_career_profile(
    *,
    repo: CareerProfileRepository,
    user_id: UUID,
    display_name: str,
) -> CareerProfile:
    profile = CareerProfile.create(user_id=user_id, display_name=display_name)
    repo.save(profile)
    return profile


def add_skill(
    *,
    profile_repo: CareerProfileRepository,
    skill_repo: SkillRepository,
    career_profile_id: UUID,
    name: str,
) -> Skill:
    profile = profile_repo.get(career_profile_id)
    if profile is None:
        raise ValueError(f"CareerProfile {career_profile_id} not found")

    skill = Skill.create(career_profile_id=career_profile_id, name=name)
    profile.add_skill(skill.id)
    skill_repo.save(skill)
    profile_repo.save(profile)
    return skill


def add_project(
    *,
    profile_repo: CareerProfileRepository,
    project_repo: ProjectRepository,
    career_profile_id: UUID,
    name: str,
    description: str | None = None,
    url: str | None = None,
) -> Project:
    profile = profile_repo.get(career_profile_id)
    if profile is None:
        raise ValueError(f"CareerProfile {career_profile_id} not found")

    project = Project.create(
        career_profile_id=career_profile_id, name=name, description=description, url=url
    )
    profile.add_project(project.id)
    project_repo.save(project)
    profile_repo.save(profile)
    return project


def add_experience(
    *,
    profile_repo: CareerProfileRepository,
    experience_repo: ExperienceRepository,
    career_profile_id: UUID,
    title: str,
    organization: str,
    description: str | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
) -> Experience:
    profile = profile_repo.get(career_profile_id)
    if profile is None:
        raise ValueError(f"CareerProfile {career_profile_id} not found")

    experience = Experience.create(
        career_profile_id=career_profile_id,
        title=title,
        organization=organization,
        description=description,
        start_date=start_date,
        end_date=end_date,
    )
    profile.add_experience(experience.id)
    experience_repo.save(experience)
    profile_repo.save(profile)
    return experience


def add_education(
    *,
    profile_repo: CareerProfileRepository,
    education_repo: EducationRepository,
    career_profile_id: UUID,
    institution: str,
    field_of_study: str | None = None,
    degree: str | None = None,
) -> Education:
    profile = profile_repo.get(career_profile_id)
    if profile is None:
        raise ValueError(f"CareerProfile {career_profile_id} not found")

    education = Education.create(
        career_profile_id=career_profile_id,
        institution=institution,
        field_of_study=field_of_study,
        degree=degree,
    )
    profile.add_education(education.id)
    education_repo.save(education)
    profile_repo.save(profile)
    return education


def add_certification(
    *,
    profile_repo: CareerProfileRepository,
    certification_repo: CertificationRepository,
    career_profile_id: UUID,
    name: str,
    issuer: str | None = None,
    issued_at: datetime | None = None,
) -> Certification:
    profile = profile_repo.get(career_profile_id)
    if profile is None:
        raise ValueError(f"CareerProfile {career_profile_id} not found")

    certification = Certification.create(
        career_profile_id=career_profile_id, name=name, issuer=issuer, issued_at=issued_at
    )
    profile.add_certification(certification.id)
    certification_repo.save(certification)
    profile_repo.save(profile)
    return certification


def register_evidence_source(
    *,
    source_repo: EvidenceSourceRepository,
    source_type: EvidenceSourceType,
    source_label: str,
    source_uri: str | None = None,
) -> EvidenceSource:
    if source_uri:
        existing = source_repo.get_by_uri(source_type, source_uri)
        if existing is not None:
            return existing

    source = EvidenceSource.create(
        source_type=source_type,
        label=source_label,
        uri=source_uri,
    )
    source_repo.save(source)
    return source


def link_evidence(
    *,
    evidence_repo: EvidenceRepository,
    source_repo: EvidenceSourceRepository,
    subject_type: EvidenceSubjectType,
    subject_id: UUID,
    evidence_source_id: UUID,
    excerpt: str | None = None,
    relevance_note: str | None = None,
) -> Evidence:
    source = source_repo.get(evidence_source_id)
    if source is None:
        raise ValueError(f"EvidenceSource {evidence_source_id} not found")

    evidence = Evidence.create(
        subject_type=subject_type,
        subject_id=subject_id,
        evidence_source_id=evidence_source_id,
        excerpt=excerpt,
        relevance_note=relevance_note,
    )
    evidence_repo.save(evidence)
    return evidence


def attach_evidence_to_skill(
    *,
    skill_repo: SkillRepository,
    source_repo: EvidenceSourceRepository,
    evidence_repo: EvidenceRepository,
    skill_id: UUID,
    source_type: EvidenceSourceType,
    source_label: str,
    source_uri: str | None = None,
    excerpt: str | None = None,
    relevance_note: str | None = None,
) -> Evidence:
    """Register/reuse a source and create a subject-specific evidence link."""

    skill = skill_repo.get(skill_id)
    if skill is None:
        raise ValueError(f"Skill {skill_id} not found")

    source = register_evidence_source(
        source_repo=source_repo,
        source_type=source_type,
        source_label=source_label,
        source_uri=source_uri,
    )
    return link_evidence(
        evidence_repo=evidence_repo,
        source_repo=source_repo,
        subject_type=EvidenceSubjectType.SKILL,
        subject_id=skill.id,
        evidence_source_id=source.id,
        excerpt=excerpt,
        relevance_note=relevance_note,
    )
