"""Optional Postgres integration tests.

Set TEST_DATABASE_URL and run `alembic upgrade head` before running this file.
The suite is skipped when no test database is configured, so the normal unit
suite remains runnable without Postgres.
"""

from __future__ import annotations

import os
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.domain.entities import CareerProfile, Evidence, EvidenceSource, Skill
from app.domain.value_objects import EvidenceSourceType, EvidenceSubjectType
from app.infrastructure.db.models import EvidenceModel, EvidenceSourceModel
from app.infrastructure.db.repositories import (
    SqlAlchemyCareerProfileRepository,
    SqlAlchemyEvidenceRepository,
    SqlAlchemyEvidenceSourceRepository,
    SqlAlchemySkillRepository,
)

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")
pytestmark = pytest.mark.skipif(not TEST_DATABASE_URL, reason="TEST_DATABASE_URL is not configured")


def test_postgres_persists_profile_skill_and_reused_source():
    engine = create_engine(TEST_DATABASE_URL, future=True)
    with Session(engine) as session:
        profile_repo = SqlAlchemyCareerProfileRepository(session)
        skill_repo = SqlAlchemySkillRepository(session)
        source_repo = SqlAlchemyEvidenceSourceRepository(session)
        evidence_repo = SqlAlchemyEvidenceRepository(session)

        profile = CareerProfile.create(user_id=uuid4(), display_name="Integration Test")
        profile_repo.save(profile)

        skill = Skill.create(career_profile_id=profile.id, name="Python")
        profile.add_skill(skill.id)
        skill_repo.save(skill)
        profile_repo.save(profile)

        source = EvidenceSource.create(
            source_type=EvidenceSourceType.GITHUB,
            label="GitHub: test",
            uri="https://github.com/example/hadence-test",
        )
        source_repo.save(source)

        evidence = Evidence.create(
            subject_type=EvidenceSubjectType.SKILL,
            subject_id=skill.id,
            evidence_source_id=source.id,
            excerpt="Python is used here",
        )
        evidence_repo.save(evidence)

        loaded = profile_repo.get(profile.id)
        assert loaded is not None
        assert skill.id in loaded.skill_ids

        loaded_source = source_repo.get_by_uri(
            EvidenceSourceType.GITHUB, "https://github.com/example/hadence-test"
        )
        assert loaded_source is not None
        assert loaded_source.id == source.id

        loaded_evidence = evidence_repo.list_for_subject("skill", skill.id)
        assert loaded_evidence[0].id == evidence.id

        # Verify directly at the ORM layer that the rows are actually persistent.
        assert session.execute(select(EvidenceSourceModel)).scalars().first() is not None
        assert session.execute(select(EvidenceModel)).scalars().first() is not None

    engine.dispose()
