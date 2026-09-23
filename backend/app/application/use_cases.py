"""Application-layer use cases for the Hadence Career Evidence Foundation."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
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
from app.domain.value_objects import AssessmentLevel, EvidenceSourceType, EvidenceSubjectType


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


@dataclass(frozen=True)
class GitHubCollectionResult:
    """Outcome of running the GitHub Evidence Collector once.

    `linked_evidence` only ever links to skills the user already claimed —
    see `collect_github_evidence`'s docstring for why. `suggested_skills`
    surfaces languages GitHub reports that have no matching skill yet, as
    plain names for the user to review and decide whether to add
    themselves — Hadence never adds them on the user's behalf.
    """

    linked_evidence: list[Evidence]
    suggested_skills: list[str]


def collect_github_evidence(
    *,
    profile_repo: CareerProfileRepository,
    skill_repo: SkillRepository,
    source_repo: EvidenceSourceRepository,
    evidence_repo: EvidenceRepository,
    github_client: GitHubClient,
    career_profile_id: UUID,
    github_username: str,
) -> GitHubCollectionResult:
    """Fetch a GitHub user's public repositories and turn them into evidence.

    Deliberately does NOT create new skills. A repository written in a
    language the user hasn't claimed as a skill is not evidence of a claim
    Hadence is allowed to make on the user's behalf — see docs/domain-model.md
    §1 and the "no unsupported career claims" product principle. Such
    languages are returned as `suggested_skills` instead; the user (or a
    later use case, once they explicitly add the skill) decides.

    Forked repositories are skipped — a fork is not evidence of the user's
    own work. Repeated calls are safe: `register_evidence_source` reuses an
    existing source for the same repo URL, and this use case skips creating
    a second Evidence row for a skill that's already linked to that source.
    """

    profile = profile_repo.get(career_profile_id)
    if profile is None:
        raise ValueError(f"CareerProfile {career_profile_id} not found")

    skills_by_lower_name = {s.name.lower(): s for s in skill_repo.list_for_profile(profile.id)}

    linked_evidence: list[Evidence] = []
    suggested_skills: set[str] = set()

    for repo in github_client.list_public_repositories(github_username):
        if repo.is_fork or not repo.primary_language:
            continue

        skill = skills_by_lower_name.get(repo.primary_language.lower())
        if skill is None:
            suggested_skills.add(repo.primary_language)
            continue

        source = register_evidence_source(
            source_repo=source_repo,
            source_type=EvidenceSourceType.GITHUB,
            source_label=f"GitHub: {repo.name}",
            source_uri=repo.html_url,
        )

        already_linked = any(
            e.evidence_source_id == source.id
            for e in evidence_repo.list_for_subject(EvidenceSubjectType.SKILL, skill.id)
        )
        if already_linked:
            continue

        evidence = link_evidence(
            evidence_repo=evidence_repo,
            source_repo=source_repo,
            subject_type=EvidenceSubjectType.SKILL,
            subject_id=skill.id,
            evidence_source_id=source.id,
            excerpt=f"{repo.primary_language} is the primary language of this repository",
            relevance_note="Detected by the GitHub Evidence Collector",
        )
        linked_evidence.append(evidence)

    return GitHubCollectionResult(
        linked_evidence=linked_evidence, suggested_skills=sorted(suggested_skills)
    )


def create_job(
    *,
    job_repo: JobRepository,
    title: str,
    company: str,
    raw_description: str,
    source_url: str | None = None,
) -> Job:
    job = Job.create(
        title=title, company=company, raw_description=raw_description, source_url=source_url
    )
    job_repo.save(job)
    return job


def extract_job_requirements(
    *,
    job_repo: JobRepository,
    requirement_repo: JobRequirementRepository,
    llm_provider: LLMProvider,
    job_id: UUID,
) -> list[JobRequirement]:
    """Extract structured requirements from a Job's raw_description via the LLM.

    Every extracted item is checked against the Job's actual raw_description
    before being saved: if the model's `source_quote` doesn't appear
    verbatim in the source text, that item is discarded rather than saved
    as an unverifiable requirement. This applies 'no unsupported claims' to
    Hadence's own AI output, not just to what a user claims about
    themselves — see docs/domain-model.md §2 and
    app/domain/ports/llm_provider.py.
    """

    job = job_repo.get(job_id)
    if job is None:
        raise ValueError(f"Job {job_id} not found")

    extracted = llm_provider.extract_job_requirements(job.raw_description)

    saved: list[JobRequirement] = []
    for item in extracted:
        if item.source_quote not in job.raw_description:
            continue  # ungrounded — the model's quote doesn't match the source text
        requirement = JobRequirement.create(
            job_id=job.id,
            text=item.text,
            requirement_type=item.requirement_type,
            source_quote=item.source_quote,
        )
        requirement_repo.save(requirement)
        saved.append(requirement)

    return saved


def _skill_matches_requirement(skill_name: str, requirement_text: str) -> bool:
    """Whole-word, case-insensitive containment — 'Python' matches 'Python'
    or 'Python developer', but not 'CPython' (word-boundary check)."""

    pattern = rf"\b{re.escape(skill_name.lower())}\b"
    return re.search(pattern, requirement_text.lower()) is not None


def _find_matching_skill(requirement_text: str, skills: list[Skill]) -> Skill | None:
    for skill in skills:
        if _skill_matches_requirement(skill.name, requirement_text):
            return skill
    return None


def _assess_from_evidence_count(evidence_count: int) -> AssessmentLevel:
    if evidence_count == 0:
        return AssessmentLevel.WEAK
    if evidence_count == 1:
        return AssessmentLevel.PARTIAL
    return AssessmentLevel.STRONG


def _build_explanation(
    requirement_text: str, skill: Skill | None, evidence_list: list[Evidence]
) -> str:
    if skill is None:
        return f'No skill in the profile matches "{requirement_text}".'
    if not evidence_list:
        return f'"{skill.name}" is listed as a skill, but has no supporting evidence attached.'

    excerpts = [e.excerpt for e in evidence_list if e.excerpt]
    detail = "; ".join(excerpts[:3]) if excerpts else "see the attached evidence sources"
    count = len(evidence_list)
    piece_word = "piece" if count == 1 else "pieces"
    return f'"{skill.name}" is backed by {count} {piece_word} of evidence: {detail}.'


def map_job_requirements_to_evidence(
    *,
    job_repo: JobRepository,
    requirement_repo: JobRequirementRepository,
    skill_repo: SkillRepository,
    evidence_repo: EvidenceRepository,
    requirement_evidence_repo: RequirementEvidenceRepository,
    job_id: UUID,
    career_profile_id: UUID,
) -> list[RequirementEvidence]:
    """The heart of the product: for each of a Job's requirements, find
    whether the CareerProfile has a matching, evidence-backed skill, and
    record a deterministic, explainable assessment.

    Deliberately rule-based, not LLM-based — see the architecture
    discussion this was built from: matching a requirement's text to a
    skill name and counting real Evidence records is a lookup/counting
    operation, not an interpretive one, so plain code is more reliable,
    faster, and free (see docs/architecture.md §4 and the brief's AI usage
    philosophy). The trade-off is real and documented: a requirement
    phrased without a skill name in it (e.g. "5+ years of backend
    experience") won't match anything today and is scored None. Improving
    that is future work (e.g. LLM-assisted matching), not a bug in this
    version.

    Assessment rule (see docs/domain-model.md §4 for what each level means):
    - No matching skill in the profile at all -> None
    - Matching skill exists but has zero Evidence records -> Weak
    - Matching skill exists with exactly one Evidence record -> Partial
    - Matching skill exists with two or more Evidence records -> Strong
    'Conflicting' is not auto-assigned in this version — there is no
    conflict-detection heuristic yet.

    Re-running this for the same job/profile updates each requirement's
    existing RequirementEvidence in place (see
    RequirementEvidenceRepository.save) rather than accumulating duplicate
    assessments, since the profile's evidence can grow between runs.
    """

    job = job_repo.get(job_id)
    if job is None:
        raise ValueError(f"Job {job_id} not found")

    requirements = requirement_repo.list_for_job(job_id)
    if not requirements:
        raise ValueError(f"Job {job_id} has no extracted requirements yet — run extraction first")

    skills = skill_repo.list_for_profile(career_profile_id)

    results: list[RequirementEvidence] = []
    for requirement in requirements:
        matched_skill = _find_matching_skill(requirement.text, skills)

        if matched_skill is None:
            evidence_list: list[Evidence] = []
        else:
            evidence_list = evidence_repo.list_for_subject(
                EvidenceSubjectType.SKILL, matched_skill.id
            )

        evidence_ids = [e.id for e in evidence_list]
        assessment = (
            AssessmentLevel.NONE
            if matched_skill is None
            else _assess_from_evidence_count(len(evidence_list))
        )
        explanation = _build_explanation(requirement.text, matched_skill, evidence_list)

        requirement_evidence = RequirementEvidence.create(
            job_requirement_id=requirement.id,
            evidence_ids=evidence_ids,
            assessment=assessment,
            explanation=explanation,
        )
        requirement_evidence_repo.save(requirement_evidence)
        results.append(requirement_evidence)

    return results
