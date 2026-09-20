from uuid import uuid4

import pytest

from app.application.use_cases import (
    add_certification,
    add_education,
    add_experience,
    add_project,
    add_skill,
    attach_evidence_to_skill,
    collect_github_evidence,
    create_career_profile,
    create_job,
    extract_job_requirements,
    link_evidence,
    register_evidence_source,
)
from app.domain.ports.github_client import GitHubRepositoryInfo
from app.domain.ports.llm_provider import ExtractedRequirement
from app.domain.value_objects import EvidenceSourceType, EvidenceSubjectType, RequirementType
from app.infrastructure.db.in_memory import (
    InMemoryCareerProfileRepository,
    InMemoryCertificationRepository,
    InMemoryEducationRepository,
    InMemoryEvidenceRepository,
    InMemoryEvidenceSourceRepository,
    InMemoryExperienceRepository,
    InMemoryJobRepository,
    InMemoryJobRequirementRepository,
    InMemoryProjectRepository,
    InMemorySkillRepository,
)
from app.infrastructure.integrations.github.fake import FakeGitHubClient
from app.infrastructure.llm.fake import FakeLLMProvider


@pytest.fixture
def repos():
    return {
        "profile": InMemoryCareerProfileRepository(),
        "skill": InMemorySkillRepository(),
        "project": InMemoryProjectRepository(),
        "experience": InMemoryExperienceRepository(),
        "education": InMemoryEducationRepository(),
        "certification": InMemoryCertificationRepository(),
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


def test_add_project_links_it_to_the_profile(repos):
    profile = create_career_profile(repo=repos["profile"], user_id=uuid4(), display_name="Metehan")

    project = add_project(
        profile_repo=repos["profile"],
        project_repo=repos["project"],
        career_profile_id=profile.id,
        name="SyntheticData",
        description="A synthetic data generation project",
        url="https://github.com/example/synthetic-data",
    )

    updated_profile = repos["profile"].get(profile.id)
    assert project.id in updated_profile.project_ids
    assert repos["project"].get(project.id) is not None


def test_add_project_raises_for_unknown_profile(repos):
    with pytest.raises(ValueError):
        add_project(
            profile_repo=repos["profile"],
            project_repo=repos["project"],
            career_profile_id=uuid4(),
            name="SyntheticData",
        )


def test_add_experience_links_it_to_the_profile(repos):
    profile = create_career_profile(repo=repos["profile"], user_id=uuid4(), display_name="Metehan")

    experience = add_experience(
        profile_repo=repos["profile"],
        experience_repo=repos["experience"],
        career_profile_id=profile.id,
        title="Data Analyst",
        organization="Acme",
    )

    updated_profile = repos["profile"].get(profile.id)
    assert experience.id in updated_profile.experience_ids


def test_add_education_links_it_to_the_profile(repos):
    profile = create_career_profile(repo=repos["profile"], user_id=uuid4(), display_name="Metehan")

    education = add_education(
        profile_repo=repos["profile"],
        education_repo=repos["education"],
        career_profile_id=profile.id,
        institution="Dokuz Eylul University",
    )

    updated_profile = repos["profile"].get(profile.id)
    assert education.id in updated_profile.education_ids


def test_add_certification_links_it_to_the_profile(repos):
    profile = create_career_profile(repo=repos["profile"], user_id=uuid4(), display_name="Metehan")

    certification = add_certification(
        profile_repo=repos["profile"],
        certification_repo=repos["certification"],
        career_profile_id=profile.id,
        name="AWS Certified Developer",
    )

    updated_profile = repos["profile"].get(profile.id)
    assert certification.id in updated_profile.certification_ids


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


def test_register_evidence_source_without_uri_always_creates_new(repos):
    first = register_evidence_source(
        source_repo=repos["source"],
        source_type=EvidenceSourceType.MANUAL,
        source_label="manual note",
    )
    second = register_evidence_source(
        source_repo=repos["source"],
        source_type=EvidenceSourceType.MANUAL,
        source_label="manual note",
    )

    assert first.id != second.id


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


def test_one_source_can_support_multiple_subjects_without_duplication(repos):
    profile = create_career_profile(repo=repos["profile"], user_id=uuid4(), display_name="Metehan")
    skill = add_skill(
        profile_repo=repos["profile"],
        skill_repo=repos["skill"],
        career_profile_id=profile.id,
        name="Python",
    )
    project = add_project(
        profile_repo=repos["profile"],
        project_repo=repos["project"],
        career_profile_id=profile.id,
        name="SyntheticData",
    )
    project_id = project.id
    source = register_evidence_source(
        source_repo=repos["source"],
        source_type=EvidenceSourceType.GITHUB,
        source_label="GitHub: SyntheticData",
        source_uri="https://github.com/example/synthetic-data",
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

    assert skill_evidence.evidence_source_id == project_evidence.evidence_source_id
    assert len(repos["evidence"].list_for_subject("skill", skill.id)) == 1
    assert len(repos["evidence"].list_for_subject("project", project_id)) == 1


def test_link_evidence_raises_for_unknown_source(repos):
    with pytest.raises(ValueError):
        link_evidence(
            evidence_repo=repos["evidence"],
            source_repo=repos["source"],
            subject_type=EvidenceSubjectType.SKILL,
            subject_id=uuid4(),
            evidence_source_id=uuid4(),
        )


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


def test_collect_github_evidence_links_matching_skill():
    repos = {
        "profile": InMemoryCareerProfileRepository(),
        "skill": InMemorySkillRepository(),
        "source": InMemoryEvidenceSourceRepository(),
        "evidence": InMemoryEvidenceRepository(),
    }
    github = FakeGitHubClient()
    profile = create_career_profile(repo=repos["profile"], user_id=uuid4(), display_name="Metehan")
    skill = add_skill(
        profile_repo=repos["profile"],
        skill_repo=repos["skill"],
        career_profile_id=profile.id,
        name="Python",
    )
    github.seed(
        "mpinarbasii",
        [
            GitHubRepositoryInfo(
                name="synthetic-data",
                html_url="https://github.com/mpinarbasii/synthetic-data",
                description="A synthetic data generator",
                primary_language="Python",
                is_fork=False,
            )
        ],
    )

    result = collect_github_evidence(
        profile_repo=repos["profile"],
        skill_repo=repos["skill"],
        source_repo=repos["source"],
        evidence_repo=repos["evidence"],
        github_client=github,
        career_profile_id=profile.id,
        github_username="mpinarbasii",
    )

    assert len(result.linked_evidence) == 1
    assert result.linked_evidence[0].subject_id == skill.id
    assert result.suggested_skills == []


def test_collect_github_evidence_suggests_unclaimed_language_without_creating_skill():
    repos = {
        "profile": InMemoryCareerProfileRepository(),
        "skill": InMemorySkillRepository(),
        "source": InMemoryEvidenceSourceRepository(),
        "evidence": InMemoryEvidenceRepository(),
    }
    github = FakeGitHubClient()
    profile = create_career_profile(repo=repos["profile"], user_id=uuid4(), display_name="Metehan")
    github.seed(
        "mpinarbasii",
        [
            GitHubRepositoryInfo(
                name="rust-cli",
                html_url="https://github.com/mpinarbasii/rust-cli",
                description=None,
                primary_language="Rust",
                is_fork=False,
            )
        ],
    )

    result = collect_github_evidence(
        profile_repo=repos["profile"],
        skill_repo=repos["skill"],
        source_repo=repos["source"],
        evidence_repo=repos["evidence"],
        github_client=github,
        career_profile_id=profile.id,
        github_username="mpinarbasii",
    )

    assert result.linked_evidence == []
    assert result.suggested_skills == ["Rust"]
    # No skill was silently created — see collect_github_evidence's docstring.
    assert repos["skill"].list_for_profile(profile.id) == []


def test_collect_github_evidence_skips_forks():
    repos = {
        "profile": InMemoryCareerProfileRepository(),
        "skill": InMemorySkillRepository(),
        "source": InMemoryEvidenceSourceRepository(),
        "evidence": InMemoryEvidenceRepository(),
    }
    github = FakeGitHubClient()
    profile = create_career_profile(repo=repos["profile"], user_id=uuid4(), display_name="Metehan")
    add_skill(
        profile_repo=repos["profile"],
        skill_repo=repos["skill"],
        career_profile_id=profile.id,
        name="Python",
    )
    github.seed(
        "mpinarbasii",
        [
            GitHubRepositoryInfo(
                name="forked-repo",
                html_url="https://github.com/mpinarbasii/forked-repo",
                description=None,
                primary_language="Python",
                is_fork=True,
            )
        ],
    )

    result = collect_github_evidence(
        profile_repo=repos["profile"],
        skill_repo=repos["skill"],
        source_repo=repos["source"],
        evidence_repo=repos["evidence"],
        github_client=github,
        career_profile_id=profile.id,
        github_username="mpinarbasii",
    )

    assert result.linked_evidence == []
    assert result.suggested_skills == []


def test_collect_github_evidence_is_idempotent_across_repeated_runs():
    repos = {
        "profile": InMemoryCareerProfileRepository(),
        "skill": InMemorySkillRepository(),
        "source": InMemoryEvidenceSourceRepository(),
        "evidence": InMemoryEvidenceRepository(),
    }
    github = FakeGitHubClient()
    profile = create_career_profile(repo=repos["profile"], user_id=uuid4(), display_name="Metehan")
    add_skill(
        profile_repo=repos["profile"],
        skill_repo=repos["skill"],
        career_profile_id=profile.id,
        name="Python",
    )
    github.seed(
        "mpinarbasii",
        [
            GitHubRepositoryInfo(
                name="synthetic-data",
                html_url="https://github.com/mpinarbasii/synthetic-data",
                description=None,
                primary_language="Python",
                is_fork=False,
            )
        ],
    )
    kwargs = dict(
        profile_repo=repos["profile"],
        skill_repo=repos["skill"],
        source_repo=repos["source"],
        evidence_repo=repos["evidence"],
        github_client=github,
        career_profile_id=profile.id,
        github_username="mpinarbasii",
    )

    first_result = collect_github_evidence(**kwargs)
    second_result = collect_github_evidence(**kwargs)

    assert len(first_result.linked_evidence) == 1
    assert len(second_result.linked_evidence) == 0  # already linked, not duplicated
    linked_skill_evidence = repos["evidence"].list_for_subject(
        EvidenceSubjectType.SKILL, first_result.linked_evidence[0].subject_id
    )
    assert len(linked_skill_evidence) == 1  # still just one Evidence row after two runs


def test_collect_github_evidence_raises_for_unknown_profile():
    repos = {
        "profile": InMemoryCareerProfileRepository(),
        "skill": InMemorySkillRepository(),
        "source": InMemoryEvidenceSourceRepository(),
        "evidence": InMemoryEvidenceRepository(),
    }
    with pytest.raises(ValueError):
        collect_github_evidence(
            profile_repo=repos["profile"],
            skill_repo=repos["skill"],
            source_repo=repos["source"],
            evidence_repo=repos["evidence"],
            github_client=FakeGitHubClient(),
            career_profile_id=uuid4(),
            github_username="mpinarbasii",
        )


def test_collect_github_evidence_propagates_user_not_found():
    from app.domain.ports.github_client import GitHubUserNotFoundError

    repos = {
        "profile": InMemoryCareerProfileRepository(),
        "skill": InMemorySkillRepository(),
        "source": InMemoryEvidenceSourceRepository(),
        "evidence": InMemoryEvidenceRepository(),
    }
    github = FakeGitHubClient()
    github.seed_not_found("ghost-user")
    profile = create_career_profile(repo=repos["profile"], user_id=uuid4(), display_name="Metehan")

    with pytest.raises(GitHubUserNotFoundError):
        collect_github_evidence(
            profile_repo=repos["profile"],
            skill_repo=repos["skill"],
            source_repo=repos["source"],
            evidence_repo=repos["evidence"],
            github_client=github,
            career_profile_id=profile.id,
            github_username="ghost-user",
        )


def test_create_job_preserves_raw_description():
    job_repo = InMemoryJobRepository()

    job = create_job(
        job_repo=job_repo,
        title="Backend Engineer",
        company="Acme",
        raw_description="We need a Python developer with 5+ years of experience.",
    )

    assert job_repo.get(job.id) is job
    assert job.raw_description == "We need a Python developer with 5+ years of experience."


def test_extract_job_requirements_saves_grounded_requirements():
    job_repo = InMemoryJobRepository()
    requirement_repo = InMemoryJobRequirementRepository()
    llm = FakeLLMProvider()

    raw_description = "We need a Python developer with 5+ years of experience. SQL is a plus."
    job = create_job(
        job_repo=job_repo, title="Backend Engineer", company="Acme", raw_description=raw_description
    )
    llm.seed_extraction(
        raw_description,
        [
            ExtractedRequirement(
                text="Python",
                requirement_type=RequirementType.REQUIRED,
                source_quote="Python developer with 5+ years of experience",
            ),
            ExtractedRequirement(
                text="SQL",
                requirement_type=RequirementType.PREFERRED,
                source_quote="SQL is a plus",
            ),
        ],
    )

    saved = extract_job_requirements(
        job_repo=job_repo, requirement_repo=requirement_repo, llm_provider=llm, job_id=job.id
    )

    assert len(saved) == 2
    assert {r.text for r in saved} == {"Python", "SQL"}
    assert len(requirement_repo.list_for_job(job.id)) == 2


def test_extract_job_requirements_discards_ungrounded_quotes():
    """The core safety guarantee: if the model's source_quote doesn't
    actually appear in the job's raw_description, that requirement is
    dropped rather than saved as an unverifiable claim."""

    job_repo = InMemoryJobRepository()
    requirement_repo = InMemoryJobRequirementRepository()
    llm = FakeLLMProvider()

    raw_description = "We need a Python developer."
    job = create_job(
        job_repo=job_repo, title="Backend Engineer", company="Acme", raw_description=raw_description
    )
    llm.seed_extraction(
        raw_description,
        [
            ExtractedRequirement(
                text="Python",
                requirement_type=RequirementType.REQUIRED,
                source_quote="Python developer",  # genuinely in the text
            ),
            ExtractedRequirement(
                text="Kubernetes",
                requirement_type=RequirementType.REQUIRED,
                source_quote="Kubernetes experience required",  # hallucinated — not in the text
            ),
        ],
    )

    saved = extract_job_requirements(
        job_repo=job_repo, requirement_repo=requirement_repo, llm_provider=llm, job_id=job.id
    )

    assert len(saved) == 1
    assert saved[0].text == "Python"
    assert requirement_repo.list_for_job(job.id) == saved


def test_extract_job_requirements_raises_for_unknown_job():
    job_repo = InMemoryJobRepository()
    requirement_repo = InMemoryJobRequirementRepository()
    llm = FakeLLMProvider()

    with pytest.raises(ValueError):
        extract_job_requirements(
            job_repo=job_repo, requirement_repo=requirement_repo, llm_provider=llm, job_id=uuid4()
        )
