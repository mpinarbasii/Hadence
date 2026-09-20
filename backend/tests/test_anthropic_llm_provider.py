"""Tests for the pure JSON-parsing logic in the Anthropic provider.

Deliberately does not call the real Anthropic API — these test
`_parse_requirements_response` directly, which is exactly why that
function is split out from the class (see anthropic_provider.py).
"""

from __future__ import annotations

import json

import pytest

from app.domain.ports.llm_provider import LLMResponseError
from app.domain.value_objects import RequirementType
from app.infrastructure.llm.anthropic_provider import _parse_requirements_response


def test_parses_well_formed_response():
    response_text = json.dumps(
        [
            {
                "text": "Python",
                "requirement_type": "required",
                "source_quote": "Python developer",
            },
            {
                "text": "SQL",
                "requirement_type": "preferred",
                "source_quote": "SQL is a plus",
            },
        ]
    )

    results = _parse_requirements_response(response_text)

    assert len(results) == 2
    assert results[0].text == "Python"
    assert results[0].requirement_type == RequirementType.REQUIRED
    assert results[1].requirement_type == RequirementType.PREFERRED


def test_empty_array_is_valid():
    assert _parse_requirements_response("[]") == []


def test_invalid_json_raises_llm_response_error():
    with pytest.raises(LLMResponseError):
        _parse_requirements_response("not json at all")


def test_non_array_json_raises_llm_response_error():
    with pytest.raises(LLMResponseError):
        _parse_requirements_response(json.dumps({"not": "an array"}))


def test_skips_entries_with_unknown_requirement_type():
    response_text = json.dumps(
        [
            {"text": "Python", "requirement_type": "required", "source_quote": "Python"},
            {"text": "Bad", "requirement_type": "not_a_real_type", "source_quote": "Bad"},
        ]
    )

    results = _parse_requirements_response(response_text)

    assert len(results) == 1
    assert results[0].text == "Python"


def test_skips_entries_missing_fields():
    response_text = json.dumps(
        [
            {"text": "Python", "requirement_type": "required", "source_quote": "Python"},
            {"text": "Missing quote", "requirement_type": "required"},
        ]
    )

    results = _parse_requirements_response(response_text)

    assert len(results) == 1


def test_skips_non_object_entries():
    response_text = json.dumps(
        [
            {"text": "Python", "requirement_type": "required", "source_quote": "Python"},
            "just a string, not an object",
        ]
    )

    results = _parse_requirements_response(response_text)

    assert len(results) == 1
