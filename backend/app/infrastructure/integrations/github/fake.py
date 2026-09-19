"""Fake GitHubClient for fast unit/API tests — no real network calls."""

from __future__ import annotations

from app.domain.ports.github_client import (
    GitHubApiError,
    GitHubRepositoryInfo,
    GitHubUserNotFoundError,
)


class FakeGitHubClient:
    def __init__(self) -> None:
        self._repos_by_username: dict[str, list[GitHubRepositoryInfo]] = {}
        self._raise_not_found: set[str] = set()
        self._raise_api_error: set[str] = set()

    def seed(self, username: str, repos: list[GitHubRepositoryInfo]) -> None:
        self._repos_by_username[username] = repos

    def seed_not_found(self, username: str) -> None:
        self._raise_not_found.add(username)

    def seed_api_error(self, username: str) -> None:
        self._raise_api_error.add(username)

    def list_public_repositories(self, username: str) -> list[GitHubRepositoryInfo]:
        if username in self._raise_not_found:
            raise GitHubUserNotFoundError(f"GitHub user '{username}' not found")
        if username in self._raise_api_error:
            raise GitHubApiError("simulated GitHub API failure")
        return self._repos_by_username.get(username, [])
