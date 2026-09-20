"""LLM provider abstraction.

The application layer depends only on this interface, never on a specific
vendor SDK. Implementations live in infrastructure/llm/ (AnthropicLLMProvider
is the first one; a FakeLLMProvider lives alongside it for tests).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from app.domain.value_objects import RequirementType


@dataclass(frozen=True)
class ExtractedRequirement:
    """One requirement as an LLM extracted it from a job description.

    `source_quote` must be a verbatim substring of the original text — see
    app/application/use_cases.py:extract_job_requirements, which verifies
    this before trusting the extraction. An LLM can hallucinate a quote
    that isn't actually in the source; Hadence checks its own AI's output
    against the same 'no unsupported claims' standard it applies to users.
    """

    text: str
    requirement_type: RequirementType
    source_quote: str


class LLMResponseError(Exception):
    """The model's response could not be parsed into the expected shape."""


class LLMProvider(Protocol):
    def complete(self, prompt: str, *, max_tokens: int = 1000) -> str:
        """Return a plain-text completion for the given prompt."""
        ...

    def extract_job_requirements(self, raw_description: str) -> list[ExtractedRequirement]:
        """Extract structured requirements from an unstructured job posting.

        Raises LLMResponseError if the model's response can't be parsed.
        Individual malformed entries within an otherwise-valid response are
        skipped rather than failing the whole extraction — see the
        implementation's parsing logic.
        """
        ...
