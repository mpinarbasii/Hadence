"""GitHub REST API v3 client — the only place that knows GitHub's response shape."""

from __future__ import annotations

import httpx

from app.domain.ports.github_client import (
    GitHubApiError,
    GitHubRepositoryInfo,
    GitHubUserNotFoundError,
)

_API_BASE = "https://api.github.com"


class HttpGitHubClient:
    """Uses the token if provided (higher rate limit); works without one too
    (60 requests/hour, unauthenticated) — see app/config.py:github_token."""

    def __init__(self, token: str | None = None, timeout: float = 10.0) -> None:
        self._token = token
        self._timeout = timeout

    def _headers(self) -> dict[str, str]:
        headers = {"Accept": "application/vnd.github+json"}
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"
        return headers

    def list_public_repositories(self, username: str) -> list[GitHubRepositoryInfo]:
        try:
            response = httpx.get(
                f"{_API_BASE}/users/{username}/repos",
                params={"per_page": 100, "type": "owner", "sort": "updated"},
                headers=self._headers(),
                timeout=self._timeout,
            )
        except httpx.HTTPError as exc:
            raise GitHubApiError(f"Failed to reach GitHub API: {exc}") from exc

        if response.status_code == 404:
            raise GitHubUserNotFoundError(f"GitHub user '{username}' not found")
        if response.status_code != 200:
            raise GitHubApiError(
                f"GitHub API returned {response.status_code} for user '{username}': {response.text}"
            )

        return [
            GitHubRepositoryInfo(
                name=repo["name"],
                html_url=repo["html_url"],
                description=repo.get("description"),
                primary_language=repo.get("language"),
                is_fork=bool(repo.get("fork", False)),
            )
            for repo in response.json()
        ]
