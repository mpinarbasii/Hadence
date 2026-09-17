"""LLM provider abstraction.

The application layer depends only on this interface, never on a specific
vendor SDK. Implementations (OpenAI, Anthropic, ...) live in
infrastructure/llm/. Kept minimal for now — real methods (e.g.
`extract_job_structure`, `explain_assessment`) are added in Phase 3/4 when
there's an actual use case driving the shape of the interface, instead of
guessing it upfront.
"""

from __future__ import annotations

from typing import Protocol


class LLMProvider(Protocol):
    def complete(self, prompt: str, *, max_tokens: int = 1000) -> str:
        """Return a plain-text completion for the given prompt."""
        ...
