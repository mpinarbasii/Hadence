from fastapi.testclient import TestClient

from app.api.dependencies import (
    RepositoryBundle,
    get_github_client,
    get_llm_provider,
    get_repository_bundle,
)
from app.api.main import app
from app.domain.ports.github_client import GitHubRepositoryInfo
from app.domain.ports.llm_provider import ExtractedRequirement
from app.domain.value_objects import RequirementType
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

_in_memory_bundle = RepositoryBundle(
    profile=InMemoryCareerProfileRepository(),
    skill=InMemorySkillRepository(),
    project=InMemoryProjectRepository(),
    experience=InMemoryExperienceRepository(),
    education=InMemoryEducationRepository(),
    certification=InMemoryCertificationRepository(),
    source=InMemoryEvidenceSourceRepository(),
    evidence=InMemoryEvidenceRepository(),
    job=InMemoryJobRepository(),
    job_requirement=InMemoryJobRequirementRepository(),
)
_fake_github = FakeGitHubClient()
_fake_llm = FakeLLMProvider()


def in_memory_bundle() -> RepositoryBundle:
    """Use one store throughout a multi-request API test workflow."""

    return _in_memory_bundle


def fake_github_client() -> FakeGitHubClient:
    return _fake_github


def fake_llm_provider() -> FakeLLMProvider:
    return _fake_llm


app.dependency_overrides[get_repository_bundle] = in_memory_bundle
app.dependency_overrides[get_github_client] = fake_github_client
app.dependency_overrides[get_llm_provider] = fake_llm_provider
client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_profile_then_add_skill_then_attach_evidence():
    profile_resp = client.post(
        "/profiles",
        json={
            "user_id": "11111111-1111-1111-1111-111111111111",
            "display_name": "Metehan",
        },
    )
    assert profile_resp.status_code == 200
    profile_id = profile_resp.json()["id"]

    skill_resp = client.post(f"/profiles/{profile_id}/skills", json={"name": "Python"})
    assert skill_resp.status_code == 200
    skill_id = skill_resp.json()["id"]

    evidence_resp = client.post(
        f"/skills/{skill_id}/evidence",
        json={
            "source_type": "github",
            "source_label": "GitHub: SyntheticData",
            "source_uri": "https://github.com/example/synthetic-data",
            "excerpt": "Repository written in Python",
        },
    )
    assert evidence_resp.status_code == 200
    body = evidence_resp.json()
    assert body["subject_type"] == "skill"
    assert body["subject_id"] == skill_id


def test_create_project_experience_education_certification_for_profile():
    profile_resp = client.post(
        "/profiles",
        json={
            "user_id": "22222222-2222-2222-2222-222222222222",
            "display_name": "Metehan",
        },
    )
    profile_id = profile_resp.json()["id"]

    project_resp = client.post(
        f"/profiles/{profile_id}/projects",
        json={"name": "SyntheticData", "url": "https://github.com/example/synthetic-data"},
    )
    assert project_resp.status_code == 200
    assert project_resp.json()["name"] == "SyntheticData"

    experience_resp = client.post(
        f"/profiles/{profile_id}/experiences",
        json={"title": "Data Analyst", "organization": "Acme"},
    )
    assert experience_resp.status_code == 200
    assert experience_resp.json()["organization"] == "Acme"

    education_resp = client.post(
        f"/profiles/{profile_id}/educations",
        json={"institution": "Dokuz Eylul University"},
    )
    assert education_resp.status_code == 200
    assert education_resp.json()["institution"] == "Dokuz Eylul University"

    certification_resp = client.post(
        f"/profiles/{profile_id}/certifications",
        json={"name": "AWS Certified Developer"},
    )
    assert certification_resp.status_code == 200
    assert certification_resp.json()["name"] == "AWS Certified Developer"

    profile_check = client.get(f"/profiles/{profile_id}")
    body = profile_check.json()
    assert project_resp.json()["id"] in body["project_ids"]
    assert experience_resp.json()["id"] in body["experience_ids"]
    assert education_resp.json()["id"] in body["education_ids"]
    assert certification_resp.json()["id"] in body["certification_ids"]


def test_create_project_for_unknown_profile_returns_404():
    response = client.post(
        "/profiles/00000000-0000-0000-0000-000000000000/projects", json={"name": "X"}
    )
    assert response.status_code == 404


def test_get_unknown_profile_returns_404():
    response = client.get("/profiles/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


def test_add_skill_to_unknown_profile_returns_404():
    response = client.post(
        "/profiles/00000000-0000-0000-0000-000000000000/skills", json={"name": "Python"}
    )
    assert response.status_code == 404


def test_collect_github_evidence_endpoint():
    profile_resp = client.post(
        "/profiles",
        json={
            "user_id": "44444444-4444-4444-4444-444444444444",
            "display_name": "Metehan",
        },
    )
    profile_id = profile_resp.json()["id"]
    client.post(f"/profiles/{profile_id}/skills", json={"name": "Python"})

    _fake_github.seed(
        "mpinarbasii",
        [
            GitHubRepositoryInfo(
                name="synthetic-data",
                html_url="https://github.com/mpinarbasii/synthetic-data",
                description="A synthetic data generator",
                primary_language="Python",
                is_fork=False,
            ),
            GitHubRepositoryInfo(
                name="rust-cli",
                html_url="https://github.com/mpinarbasii/rust-cli",
                description=None,
                primary_language="Rust",
                is_fork=False,
            ),
        ],
    )

    response = client.post(
        f"/profiles/{profile_id}/github-evidence", json={"github_username": "mpinarbasii"}
    )
    assert response.status_code == 200
    body = response.json()
    assert len(body["linked_evidence"]) == 1
    assert body["suggested_skills"] == ["Rust"]


def test_collect_github_evidence_returns_404_for_unknown_github_user():
    profile_resp = client.post(
        "/profiles",
        json={
            "user_id": "55555555-5555-5555-5555-555555555555",
            "display_name": "Metehan",
        },
    )
    profile_id = profile_resp.json()["id"]
    _fake_github.seed_not_found("ghost-user")

    response = client.post(
        f"/profiles/{profile_id}/github-evidence", json={"github_username": "ghost-user"}
    )
    assert response.status_code == 404


def test_create_and_get_job():
    response = client.post(
        "/jobs",
        json={
            "title": "Backend Engineer",
            "company": "Acme",
            "raw_description": "We need a Python developer with 5+ years of experience.",
        },
    )
    assert response.status_code == 200
    job_id = response.json()["id"]
    assert response.json()["raw_description"] == (
        "We need a Python developer with 5+ years of experience."
    )

    get_resp = client.get(f"/jobs/{job_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["company"] == "Acme"


def test_get_unknown_job_returns_404():
    response = client.get("/jobs/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


def test_extract_job_requirements_endpoint():
    raw_description = "We need a Python developer. SQL is a plus."
    job_resp = client.post(
        "/jobs",
        json={"title": "Backend Engineer", "company": "Acme", "raw_description": raw_description},
    )
    job_id = job_resp.json()["id"]

    _fake_llm.seed_extraction(
        raw_description,
        [
            ExtractedRequirement(
                text="Python",
                requirement_type=RequirementType.REQUIRED,
                source_quote="Python developer",
            ),
            ExtractedRequirement(
                text="SQL",
                requirement_type=RequirementType.PREFERRED,
                source_quote="SQL is a plus",
            ),
            ExtractedRequirement(
                text="Kubernetes",
                requirement_type=RequirementType.REQUIRED,
                source_quote="Kubernetes required",  # not in raw_description — must be dropped
            ),
        ],
    )

    response = client.post(f"/jobs/{job_id}/extract-requirements")
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 2
    assert {r["text"] for r in body} == {"Python", "SQL"}

    list_resp = client.get(f"/jobs/{job_id}/requirements")
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 2


def test_extract_job_requirements_returns_404_for_unknown_job():
    response = client.post("/jobs/00000000-0000-0000-0000-000000000000/extract-requirements")
    assert response.status_code == 404


def test_list_requirements_returns_404_for_unknown_job():
    response = client.get("/jobs/00000000-0000-0000-0000-000000000000/requirements")
    assert response.status_code == 404
