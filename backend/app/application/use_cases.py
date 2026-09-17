"""Use cases for the Career Evidence Foundation (Phase 1).

Each use case is a small, testable function/class that orchestrates domain
entities and repository ports. No HTTP, no ORM, no LLM SDK imports here —
only domain types and the port interfaces.
"""

from __future__ import annotations

from uuid import UUID

from app.domain.entities import CareerProfile, Evidence, EvidenceSource, Skill
from app.domain.ports.repositories import (
    CareerProfileRepository,
    EvidenceRepository,
    EvidenceSourceRepository,
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
    skill_repo.save(skill)

    profile.add_skill(skill.id)
    profile_repo.save(profile)

    return skill


def register_evidence_source(
    *,
    source_repo: EvidenceSourceRepository,
    source_type: EvidenceSourceType,
    label: str,
    uri: str | None = None,
    raw_content_ref: str | None = None,
) -> EvidenceSource:
    """Idempotently register a provenance source.

    `EvidenceSource` is a stable, reusable identity (see domain/entities.py)
    — registering the same (source_type, uri) twice returns the existing
    record instead of creating a duplicate, so the same GitHub repo, for
    example, is represented once no matter how many subjects it ends up
    supporting.

    Sources without a `uri` (e.g. a manually-typed note) cannot be
    deduplicated this way and are always created fresh.
    """
    if uri is not None:
        existing = source_repo.get_by_uri(source_type=source_type, uri=uri)
        if existing is not None:
            return existing

    source = EvidenceSource.create(
        source_type=source_type, label=label, uri=uri, raw_content_ref=raw_content_ref
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
    """Link an existing EvidenceSource to a subject (skill, project, ...).

    Each call creates its own `Evidence` row so the subject-specific
    `excerpt`/`relevance_note` stays explainable per subject, even when
    several subjects share the same `evidence_source_id` (see
    docs/domain-model.md §1 and §2).

    Deliberately does not validate that the subject itself exists — subject
    existence is each subject type's own use case's responsibility (e.g.
    `add_skill` for skills). There is no generic "subject repository" port,
    and introducing one solely for this check would be premature given only
    Skill has a real repository/use-case today.
    """
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
    """Attach evidence to an existing skill, registering the source if needed.

    Composes `register_evidence_source` + `link_evidence` so that attaching
    evidence from a source that's already registered (same source_type +
    uri) reuses that source instead of duplicating it. This is deliberately
    the *only* way evidence gets linked to a skill in Phase 1 — there is no
    path that lets a skill exist as a bare claim with no inspectable source
    (see docs/domain-model.md §1).
    """

    skill = skill_repo.get(skill_id)
    if skill is None:
        raise ValueError(f"Skill {skill_id} not found")

    source = register_evidence_source(
        source_repo=source_repo, source_type=source_type, label=source_label, uri=source_uri
    )

    return link_evidence(
        evidence_repo=evidence_repo,
        source_repo=source_repo,
        subject_type=EvidenceSubjectType.SKILL,
        subject_id=skill_id,
        evidence_source_id=source.id,
        excerpt=excerpt,
        relevance_note=relevance_note,
    )
