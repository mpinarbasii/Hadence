"""SQLAlchemy implementations of the domain repository ports."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

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
from app.domain.value_objects import EvidenceSourceType, EvidenceSubjectType
from app.infrastructure.db.models import (
    CareerProfileModel,
    CertificationModel,
    EducationModel,
    EvidenceModel,
    EvidenceSourceModel,
    ExperienceModel,
    ProjectModel,
    SkillModel,
)


def _profile_to_domain(model: CareerProfileModel) -> CareerProfile:
    return CareerProfile(
        id=model.id,
        user_id=model.user_id,
        display_name=model.display_name,
        skill_ids=[s.id for s in model.skills],
        project_ids=[p.id for p in model.projects],
        experience_ids=[e.id for e in model.experiences],
        education_ids=[e.id for e in model.educations],
        certification_ids=[c.id for c in model.certifications],
    )


class SqlAlchemyCareerProfileRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, profile: CareerProfile) -> None:
        model = self._session.get(CareerProfileModel, profile.id)
        if model is None:
            self._session.add(
                CareerProfileModel(
                    id=profile.id, user_id=profile.user_id, display_name=profile.display_name
                )
            )
        else:
            model.user_id = profile.user_id
            model.display_name = profile.display_name
        self._session.commit()

    def get(self, profile_id: UUID) -> CareerProfile | None:
        stmt = (
            select(CareerProfileModel)
            .where(CareerProfileModel.id == profile_id)
            .options(
                selectinload(CareerProfileModel.skills),
                selectinload(CareerProfileModel.projects),
                selectinload(CareerProfileModel.experiences),
                selectinload(CareerProfileModel.educations),
                selectinload(CareerProfileModel.certifications),
            )
        )
        model = self._session.execute(stmt).scalar_one_or_none()
        return None if model is None else _profile_to_domain(model)

    def get_by_user(self, user_id: UUID) -> CareerProfile | None:
        stmt = (
            select(CareerProfileModel)
            .where(CareerProfileModel.user_id == user_id)
            .options(
                selectinload(CareerProfileModel.skills),
                selectinload(CareerProfileModel.projects),
                selectinload(CareerProfileModel.experiences),
                selectinload(CareerProfileModel.educations),
                selectinload(CareerProfileModel.certifications),
            )
        )
        model = self._session.execute(stmt).scalar_one_or_none()
        return None if model is None else _profile_to_domain(model)


class SqlAlchemySkillRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, skill: Skill) -> None:
        model = self._session.get(SkillModel, skill.id)
        if model is None:
            self._session.add(
                SkillModel(id=skill.id, career_profile_id=skill.career_profile_id, name=skill.name)
            )
        else:
            model.name = skill.name
        self._session.commit()

    def get(self, skill_id: UUID) -> Skill | None:
        model = self._session.get(SkillModel, skill_id)
        if model is None:
            return None
        return Skill(id=model.id, career_profile_id=model.career_profile_id, name=model.name)

    def list_for_profile(self, career_profile_id: UUID) -> list[Skill]:
        models = (
            self._session.execute(
                select(SkillModel).where(SkillModel.career_profile_id == career_profile_id)
            )
            .scalars()
            .all()
        )
        return [Skill(id=m.id, career_profile_id=m.career_profile_id, name=m.name) for m in models]


def _source_to_domain(model: EvidenceSourceModel) -> EvidenceSource:
    return EvidenceSource(
        id=model.id,
        source_type=EvidenceSourceType(model.source_type),
        label=model.label,
        retrieved_at=model.retrieved_at,
        uri=model.uri,
        raw_content_ref=model.raw_content_ref,
        last_verified_at=model.last_verified_at,
    )


class SqlAlchemyEvidenceSourceRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, source: EvidenceSource) -> None:
        model = self._session.get(EvidenceSourceModel, source.id)
        if model is None:
            self._session.add(
                EvidenceSourceModel(
                    id=source.id,
                    source_type=source.source_type.value,
                    label=source.label,
                    uri=source.uri,
                    raw_content_ref=source.raw_content_ref,
                    retrieved_at=source.retrieved_at,
                    last_verified_at=source.last_verified_at,
                )
            )
        else:
            model.label = source.label
            model.uri = source.uri
            model.raw_content_ref = source.raw_content_ref
            model.last_verified_at = source.last_verified_at
        self._session.commit()

    def get(self, source_id: UUID) -> EvidenceSource | None:
        model = self._session.get(EvidenceSourceModel, source_id)
        return None if model is None else _source_to_domain(model)

    def get_by_uri(self, source_type: EvidenceSourceType, uri: str) -> EvidenceSource | None:
        model = self._session.execute(
            select(EvidenceSourceModel).where(
                EvidenceSourceModel.source_type == source_type.value,
                EvidenceSourceModel.uri == uri,
            )
        ).scalar_one_or_none()
        return None if model is None else _source_to_domain(model)


class SqlAlchemyEvidenceRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, evidence: Evidence) -> None:
        model = self._session.get(EvidenceModel, evidence.id)
        if model is None:
            self._session.add(
                EvidenceModel(
                    id=evidence.id,
                    subject_type=evidence.subject_type.value,
                    subject_id=evidence.subject_id,
                    evidence_source_id=evidence.evidence_source_id,
                    excerpt=evidence.excerpt,
                    relevance_note=evidence.relevance_note,
                )
            )
        else:
            model.excerpt = evidence.excerpt
            model.relevance_note = evidence.relevance_note
        self._session.commit()

    def list_for_subject(self, subject_type: str, subject_id: UUID) -> list[Evidence]:
        models = (
            self._session.execute(
                select(EvidenceModel).where(
                    EvidenceModel.subject_type == subject_type,
                    EvidenceModel.subject_id == subject_id,
                )
            )
            .scalars()
            .all()
        )
        return [
            Evidence(
                id=m.id,
                subject_type=EvidenceSubjectType(m.subject_type),
                subject_id=m.subject_id,
                evidence_source_id=m.evidence_source_id,
                excerpt=m.excerpt,
                relevance_note=m.relevance_note,
            )
            for m in models
        ]


class SqlAlchemyProjectRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, project: Project) -> None:
        model = self._session.get(ProjectModel, project.id)
        if model is None:
            self._session.add(
                ProjectModel(
                    id=project.id,
                    career_profile_id=project.career_profile_id,
                    name=project.name,
                    description=project.description,
                    url=project.url,
                )
            )
        else:
            model.name = project.name
            model.description = project.description
            model.url = project.url
        self._session.commit()

    def get(self, project_id: UUID) -> Project | None:
        model = self._session.get(ProjectModel, project_id)
        if model is None:
            return None
        return Project(
            id=model.id,
            career_profile_id=model.career_profile_id,
            name=model.name,
            description=model.description,
            url=model.url,
        )

    def list_for_profile(self, career_profile_id: UUID) -> list[Project]:
        stmt = select(ProjectModel).where(ProjectModel.career_profile_id == career_profile_id)
        models = self._session.execute(stmt).scalars().all()
        return [
            Project(
                id=m.id,
                career_profile_id=m.career_profile_id,
                name=m.name,
                description=m.description,
                url=m.url,
            )
            for m in models
        ]


class SqlAlchemyExperienceRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, experience: Experience) -> None:
        model = self._session.get(ExperienceModel, experience.id)
        if model is None:
            self._session.add(
                ExperienceModel(
                    id=experience.id,
                    career_profile_id=experience.career_profile_id,
                    title=experience.title,
                    organization=experience.organization,
                    description=experience.description,
                    start_date=experience.start_date,
                    end_date=experience.end_date,
                )
            )
        else:
            model.title = experience.title
            model.organization = experience.organization
            model.description = experience.description
            model.start_date = experience.start_date
            model.end_date = experience.end_date
        self._session.commit()

    def get(self, experience_id: UUID) -> Experience | None:
        model = self._session.get(ExperienceModel, experience_id)
        if model is None:
            return None
        return Experience(
            id=model.id,
            career_profile_id=model.career_profile_id,
            title=model.title,
            organization=model.organization,
            description=model.description,
            start_date=model.start_date,
            end_date=model.end_date,
        )

    def list_for_profile(self, career_profile_id: UUID) -> list[Experience]:
        stmt = select(ExperienceModel).where(ExperienceModel.career_profile_id == career_profile_id)
        models = self._session.execute(stmt).scalars().all()
        return [
            Experience(
                id=m.id,
                career_profile_id=m.career_profile_id,
                title=m.title,
                organization=m.organization,
                description=m.description,
                start_date=m.start_date,
                end_date=m.end_date,
            )
            for m in models
        ]


class SqlAlchemyEducationRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, education: Education) -> None:
        model = self._session.get(EducationModel, education.id)
        if model is None:
            self._session.add(
                EducationModel(
                    id=education.id,
                    career_profile_id=education.career_profile_id,
                    institution=education.institution,
                    field_of_study=education.field_of_study,
                    degree=education.degree,
                )
            )
        else:
            model.institution = education.institution
            model.field_of_study = education.field_of_study
            model.degree = education.degree
        self._session.commit()

    def get(self, education_id: UUID) -> Education | None:
        model = self._session.get(EducationModel, education_id)
        if model is None:
            return None
        return Education(
            id=model.id,
            career_profile_id=model.career_profile_id,
            institution=model.institution,
            field_of_study=model.field_of_study,
            degree=model.degree,
        )

    def list_for_profile(self, career_profile_id: UUID) -> list[Education]:
        stmt = select(EducationModel).where(EducationModel.career_profile_id == career_profile_id)
        models = self._session.execute(stmt).scalars().all()
        return [
            Education(
                id=m.id,
                career_profile_id=m.career_profile_id,
                institution=m.institution,
                field_of_study=m.field_of_study,
                degree=m.degree,
            )
            for m in models
        ]


class SqlAlchemyCertificationRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, certification: Certification) -> None:
        model = self._session.get(CertificationModel, certification.id)
        if model is None:
            self._session.add(
                CertificationModel(
                    id=certification.id,
                    career_profile_id=certification.career_profile_id,
                    name=certification.name,
                    issuer=certification.issuer,
                    issued_at=certification.issued_at,
                )
            )
        else:
            model.name = certification.name
            model.issuer = certification.issuer
            model.issued_at = certification.issued_at
        self._session.commit()

    def get(self, certification_id: UUID) -> Certification | None:
        model = self._session.get(CertificationModel, certification_id)
        if model is None:
            return None
        return Certification(
            id=model.id,
            career_profile_id=model.career_profile_id,
            name=model.name,
            issuer=model.issuer,
            issued_at=model.issued_at,
        )

    def list_for_profile(self, career_profile_id: UUID) -> list[Certification]:
        stmt = select(CertificationModel).where(
            CertificationModel.career_profile_id == career_profile_id
        )
        models = self._session.execute(stmt).scalars().all()
        return [
            Certification(
                id=m.id,
                career_profile_id=m.career_profile_id,
                name=m.name,
                issuer=m.issuer,
                issued_at=m.issued_at,
            )
            for m in models
        ]
