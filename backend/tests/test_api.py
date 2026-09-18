from fastapi.testclient import TestClient

from app.api.dependencies import RepositoryBundle, get_repository_bundle
from app.api.main import app
from app.infrastructure.db.in_memory import (
    InMemoryCareerProfileRepository,
    InMemoryEvidenceRepository,
    InMemoryEvidenceSourceRepository,
    InMemorySkillRepository,
)

_in_memory_bundle = RepositoryBundle(
    profile=InMemoryCareerProfileRepository(),
    skill=InMemorySkillRepository(),
    source=InMemoryEvidenceSourceRepository(),
    evidence=InMemoryEvidenceRepository(),
)


def in_memory_bundle() -> RepositoryBundle:
    """Use one store throughout a multi-request API test workflow."""

    return _in_memory_bundle


app.dependency_overrides[get_repository_bundle] = in_memory_bundle
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


def test_get_unknown_profile_returns_404():
    response = client.get("/profiles/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


def test_add_skill_to_unknown_profile_returns_404():
    response = client.post(
        "/profiles/00000000-0000-0000-0000-000000000000/skills", json={"name": "Python"}
    )
    assert response.status_code == 404
