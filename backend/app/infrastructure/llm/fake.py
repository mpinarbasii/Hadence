"""Fake LLMProvider for fast unit/API tests — no real API calls."""

from __future__ import annotations

from app.domain.ports.llm_provider import ExtractedRequirement


class FakeLLMProvider:
    def __init__(self) -> None:
        self._completions: dict[str, str] = {}
        self._extractions_by_description: dict[str, list[ExtractedRequirement]] = {}

    def seed_completion(self, prompt: str, response: str) -> None:
        self._completions[prompt] = response

    def seed_extraction(
        self, raw_description: str, requirements: list[ExtractedRequirement]
    ) -> None:
        self._extractions_by_description[raw_description] = requirements

    def complete(self, prompt: str, *, max_tokens: int = 1000) -> str:
        return self._completions.get(prompt, "")

    def extract_job_requirements(self, raw_description: str) -> list[ExtractedRequirement]:
        return self._extractions_by_description.get(raw_description, [])
