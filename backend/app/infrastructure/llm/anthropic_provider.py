"""Anthropic (Claude) implementation of the LLMProvider port.

The JSON-parsing logic is split into a standalone function
(`_parse_requirements_response`) specifically so it can be unit-tested
without a live API call — see tests/test_anthropic_llm_provider.py.
"""

from __future__ import annotations

import json

import anthropic

from app.domain.ports.llm_provider import ExtractedRequirement, LLMResponseError
from app.domain.value_objects import RequirementType

_EXTRACTION_SYSTEM_PROMPT = """\
You extract structured requirements from a job posting's raw text.

Respond with ONLY a JSON array (no prose, no markdown fences). Each element \
must be an object with exactly these fields:
- "text": a short, normalized requirement (e.g. "Python", "5+ years of \
backend experience")
- "requirement_type": one of "required", "preferred", "responsibility", \
"domain_signal", "education", "certification"
- "source_quote": the EXACT verbatim substring from the job posting that \
this requirement was extracted from — copied character-for-character, not \
paraphrased. This is checked against the original text, so it must match \
exactly.

If the posting has no extractable requirements, respond with an empty \
JSON array: []
"""


def _parse_requirements_response(response_text: str) -> list[ExtractedRequirement]:
    try:
        data = json.loads(response_text)
    except json.JSONDecodeError as exc:
        raise LLMResponseError(f"Model did not return valid JSON: {exc}") from exc

    if not isinstance(data, list):
        raise LLMResponseError(f"Expected a JSON array, got {type(data).__name__}")

    results: list[ExtractedRequirement] = []
    for item in data:
        if not isinstance(item, dict):
            continue  # skip malformed entries rather than fail the whole extraction
        try:
            requirement_type = RequirementType(item["requirement_type"])
            text = str(item["text"])
            source_quote = str(item["source_quote"])
        except (KeyError, ValueError):
            continue
        results.append(
            ExtractedRequirement(
                text=text, requirement_type=requirement_type, source_quote=source_quote
            )
        )
    return results


class AnthropicLLMProvider:
    def __init__(self, api_key: str, model: str = "claude-sonnet-4-6") -> None:
        self._client = anthropic.Anthropic(api_key=api_key)
        self._model = model

    def complete(self, prompt: str, *, max_tokens: int = 1000) -> str:
        response = self._client.messages.create(
            model=self._model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        return "".join(block.text for block in response.content if block.type == "text")

    def extract_job_requirements(self, raw_description: str) -> list[ExtractedRequirement]:
        response = self._client.messages.create(
            model=self._model,
            max_tokens=4000,
            system=_EXTRACTION_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": raw_description}],
        )
        response_text = "".join(block.text for block in response.content if block.type == "text")
        return _parse_requirements_response(response_text)
