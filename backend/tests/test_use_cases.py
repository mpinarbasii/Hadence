from uuid import uuid4

import pytest

from app.application.use_cases import (
    add_skill,
    attach_evidence_to_skill,
    create_career_profile,
    register_evidence_source,
)
from app.domain.value_objects import EvidenceSourceType
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


def test_register_evidence_source_is_idempotent_for_same_uri(repos):
    source1 = register_evidence_source(
        source_repo=repos["source"],
        source_type=EvidenceSourceType.GITHUB,
        source_label="GitHub: SyntheticData",
        source_uri="https://github.com/example/synthetic-data",
    )
    source2 = register_evidence_source(
        source_repo=repos["source"],
        source_type=EvidenceSourceType.GITHUB,
        source_label="Same repo, different label",
        source_uri="https://github.com/example/synthetic-data",
    )

    assert source1.id == source2.id


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


def test_two_evidence_records_can_share_one_source(repos):
    profile = create_career_profile(repo=repos["profile"], user_id=uuid4(), display_name="Metehan")
    skill1 = add_skill(
        profile_repo=repos["profile"],
        skill_repo=repos["skill"],
        career_profile_id=profile.id,
        name="Python",
    )
    skill2 = add_skill(
        profile_repo=repos["profile"],
        skill_repo=repos["skill"],
        career_profile_id=profile.id,
        name="Data Analysis",
    )

    evidence1 = attach_evidence_to_skill(
        skill_repo=repos["skill"],
        source_repo=repos["source"],
        evidence_repo=repos["evidence"],
        skill_id=skill1.id,
        source_type=EvidenceSourceType.GITHUB,
        source_label="GitHub: SyntheticData",
        source_uri="https://github.com/example/synthetic-data",
        excerpt="Python code",
    )
    evidence2 = attach_evidence_to_skill(
        skill_repo=repos["skill"],
        source_repo=repos["source"],
        evidence_repo=repos["evidence"],
        skill_id=skill2.id,
        source_type=EvidenceSourceType.GITHUB,
        source_label="GitHub: SyntheticData",
        source_uri="https://github.com/example/synthetic-data",
        excerpt="Data generation workflow",
    )

    assert evidence1.evidence_source_id == evidence2.evidence_source_id


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
