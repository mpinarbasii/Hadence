from uuid import uuid4

import pytest

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


def test_career_profile_create_has_no_skills_initially():
    profile = CareerProfile.create(user_id=uuid4(), display_name="Metehan")

    assert profile.display_name == "Metehan"
    assert profile.skill_ids == []


def test_career_profile_add_skill_prevents_duplicate_ids():
    profile = CareerProfile.create(user_id=uuid4(), display_name="Metehan")
    skill_id = uuid4()

    profile.add_skill(skill_id)

    with pytest.raises(ValueError):
        profile.add_skill(skill_id)


def test_entity_factories_create_ids():
    profile_id = uuid4()

    skill = Skill.create(career_profile_id=profile_id, name="Python")
    education = Education.create(career_profile_id=profile_id, institution="DEU")

    assert skill.id != education.id
    assert skill.career_profile_id == profile_id
    assert education.career_profile_id == profile_id


def test_evidence_source_create_sets_retrieved_at():
    source = EvidenceSource.create(
        source_type=EvidenceSourceType.GITHUB,
        label="GitHub: SyntheticData",
        uri="https://github.com/example/synthetic-data",
    )

    assert source.source_type == EvidenceSourceType.GITHUB
    assert source.retrieved_at is not None
    assert source.last_verified_at is None


def test_evidence_source_mark_verified_updates_in_place():
    source = EvidenceSource.create(source_type=EvidenceSourceType.GITHUB, label="repo")
    source_id_before = source.id

    assert source.last_verified_at is None
    source.mark_verified()

    assert source.id == source_id_before
    assert source.last_verified_at is not None


def test_project_experience_education_certification_create_factories():
    profile_id = uuid4()

    project = Project.create(career_profile_id=profile_id, name="SyntheticData")
    experience = Experience.create(
        career_profile_id=profile_id, title="Data Analyst", organization="Acme"
    )
    education = Education.create(career_profile_id=profile_id, institution="Some University")
    certification = Certification.create(career_profile_id=profile_id, name="Some Cert")

    for entity in (project, experience, education, certification):
        assert entity.id is not None
        assert entity.career_profile_id == profile_id


def test_evidence_links_subject_to_source():
    skill = Skill.create(career_profile_id=uuid4(), name="Python")
    source = EvidenceSource.create(source_type=EvidenceSourceType.GITHUB, label="repo")

    evidence = Evidence.create(
        subject_type=EvidenceSubjectType.SKILL,
        subject_id=skill.id,
        evidence_source_id=source.id,
        excerpt="Uses Python 3.11 throughout",
    )

    assert evidence.subject_id == skill.id
    assert evidence.evidence_source_id == source.id
    assert evidence.excerpt == "Uses Python 3.11 throughout"
