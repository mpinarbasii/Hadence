"""Port for fetching a user's public GitHub repository data.

The application layer depends only on this interface, never on a specific
HTTP client or the GitHub API's response shape directly — mirrors the
LLMProvider port. The real implementation lives in
infrastructure/integrations/github/client.py; a fake lives alongside it for
tests.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class GitHubRepositoryInfo:
    """A minimal, evidence-relevant projection of a GitHub repository.

    Deliberately does not carry stars/forks/watchers — those aren't
    evidence of skill, they're popularity signals, and including them would
    invite scoring logic the product explicitly avoids (see
    docs/architecture.md and the brief's "no fake confidence scores" rule).
    """

    name: str
    html_url: str
    description: str | None
    primary_language: str | None
    is_fork: bool


class GitHubUserNotFoundError(Exception):
    """The given GitHub username does not exist or has no public profile."""


class GitHubApiError(Exception):
    """The GitHub API request failed for a reason other than 'user not found'
    (rate limiting, network failure, unexpected response shape, ...)."""


class GitHubClient(Protocol):
    def list_public_repositories(self, username: str) -> list[GitHubRepositoryInfo]:
        """Return the user's public repositories as GitHub reports them,
        forks included (see GitHubRepositoryInfo.is_fork) — filtering forks
        out is a business decision, so it happens in the use case
        (collect_github_evidence), not here. Keeps this client a thin,
        honest data source.

        Raises GitHubUserNotFoundError or GitHubApiError on failure —
        callers (use cases) decide how to translate those into their own
        error handling.
        """
        ...
