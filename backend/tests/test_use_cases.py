from uuid import uuid4

import pytest

from app.application.use_cases import (
    add_skill,
    attach_evidence_to_skill,
    create_career_profile,
    link_evidence,
    register_evidence_source,
)
from app.domain.value_objects import EvidenceSourceType, EvidenceSubjectType
from app.infrastructure.db.in_memory import (
    InMemoryCareerProfileRepository,
    InMemoryEvidenceRepository,
    InMemoryEvidenceSourceRepository,
    InMemorySkillRepository,
)


@pytest.fixture
def repos():
    return {
        "profile": InMemoryCareerProfileRepository(),
        "skill": InMemorySkillRepository(),
        "source": InMemoryEvidenceSourceRepository(),
        "evidence": InMemoryEvidenceRepository(),
    }


def test_create_career_profile_persists_it(repos):
    profile = create_career_profile(repo=repos["profile"], user_id=uuid4(), display_name="Metehan")

    assert repos["profile"].get(profile.id) is profile


def test_add_skill_links_it_to_the_profile(repos):
    profile = create_career_profile(repo=repos["profile"], user_id=uuid4(), display_name="Metehan")

    skill = add_skill(
        profile_repo=repos["profile"],
        skill_repo=repos["skill"],
        career_profile_id=profile.id,
        name="Python",
    )

    updated_profile = repos["profile"].get(profile.id)
    assert skill.id in updated_profile.skill_ids


def test_add_skill_raises_for_unknown_profile(repos):
    with pytest.raises(ValueError):
        add_skill(
            profile_repo=repos["profile"],
            skill_repo=repos["skill"],
            career_profile_id=uuid4(),
            name="Python",
        )


def test_attach_evidence_creates_source_and_evidence(repos):
    profile = create_career_profile(repo=repos["profile"], user_id=uuid4(), display_name="Metehan")
    skill = add_skill(
        profile_repo=repos["profile"],
        skill_repo=repos["skill"],
        career_profile_id=profile.id,
        name="Python",
    )

    evidence = attach_evidence_to_skill(
        skill_repo=repos["skill"],
        source_repo=repos["source"],
        evidence_repo=repos["evidence"],
        skill_id=skill.id,
        source_type=EvidenceSourceType.GITHUB,
        source_label="GitHub: SyntheticData",
        source_uri="https://github.com/example/synthetic-data",
        excerpt="Repository is written in Python",
    )

    assert repos["source"].get(evidence.evidence_source_id) is not None
    stored = repos["evidence"].list_for_subject("skill", skill.id)
    assert len(stored) == 1
    assert stored[0].id == evidence.id


def test_attach_evidence_raises_for_unknown_skill(repos):
    with pytest.raises(ValueError):
        attach_evidence_to_skill(
            skill_repo=repos["skill"],
            source_repo=repos["source"],
            evidence_repo=repos["evidence"],
            skill_id=uuid4(),
            source_type=EvidenceSourceType.MANUAL,
            source_label="manual entry",
        )


def test_register_evidence_source_is_idempotent_by_uri(repos):
    first = register_evidence_source(
        source_repo=repos["source"],
        source_type=EvidenceSourceType.GITHUB,
        label="GitHub: repo-x",
        uri="https://github.com/example/repo-x",
    )
    second = register_evidence_source(
        source_repo=repos["source"],
        source_type=EvidenceSourceType.GITHUB,
        label="GitHub: repo-x (re-registered)",
        uri="https://github.com/example/repo-x",
    )

    assert first.id == second.id


def test_register_evidence_source_without_uri_always_creates_new(repos):
    first = register_evidence_source(
        source_repo=repos["source"], source_type=EvidenceSourceType.MANUAL, label="manual note"
    )
    second = register_evidence_source(
        source_repo=repos["source"], source_type=EvidenceSourceType.MANUAL, label="manual note"
    )

    assert first.id != second.id


def test_one_source_can_support_multiple_subjects_without_duplication(repos):
    """The concrete case raised in the architecture review: one GitHub repo
    supporting both a Skill and a Project must not create two EvidenceSource
    records — only two Evidence rows referencing the same source."""

    profile = create_career_profile(repo=repos["profile"], user_id=uuid4(), display_name="Metehan")
    skill = add_skill(
        profile_repo=repos["profile"],
        skill_repo=repos["skill"],
        career_profile_id=profile.id,
        name="Python",
    )
    project_id = uuid4()  # no Project repository yet — see use_cases.link_evidence docstring

    source = register_evidence_source(
        source_repo=repos["source"],
        source_type=EvidenceSourceType.GITHUB,
        label="GitHub: SyntheticData",
        uri="https://github.com/example/synthetic-data",
    )

    skill_evidence = link_evidence(
        evidence_repo=repos["evidence"],
        source_repo=repos["source"],
        subject_type=EvidenceSubjectType.SKILL,
        subject_id=skill.id,
        evidence_source_id=source.id,
        excerpt="Repository is written in Python",
    )
    project_evidence = link_evidence(
        evidence_repo=repos["evidence"],
        source_repo=repos["source"],
        subject_type=EvidenceSubjectType.PROJECT,
        subject_id=project_id,
        evidence_source_id=source.id,
        excerpt="This repository is the project itself",
    )

    # Same source, reused — not duplicated.
    assert skill_evidence.evidence_source_id == project_evidence.evidence_source_id

    skill_records = repos["evidence"].list_for_subject("skill", skill.id)
    project_records = repos["evidence"].list_for_subject("project", project_id)
    assert len(skill_records) == 1
    assert len(project_records) == 1
    # Each Evidence row keeps its own subject-specific excerpt.
    assert skill_records[0].excerpt == "Repository is written in Python"
    assert project_records[0].excerpt == "This repository is the project itself"


def test_link_evidence_raises_for_unknown_source(repos):
    with pytest.raises(ValueError):
        link_evidence(
            evidence_repo=repos["evidence"],
            source_repo=repos["source"],
            subject_type=EvidenceSubjectType.SKILL,
            subject_id=uuid4(),
            evidence_source_id=uuid4(),
        )
