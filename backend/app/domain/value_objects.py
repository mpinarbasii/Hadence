"""Value objects shared across the domain layer.

These are plain, framework-independent enums/dataclasses. No ORM, no
Pydantic-specific behavior — the domain layer must remain importable without
FastAPI, SQLAlchemy, or any LLM SDK installed.
"""

from __future__ import annotations

from enum import StrEnum


class EvidenceSourceType(StrEnum):
    RESUME = "resume"
    GITHUB = "github"
    PROJECT = "project"
    CERTIFICATE = "certificate"
    EXPERIENCE = "experience"
    MANUAL = "manual"
    PORTFOLIO = "portfolio"


class EvidenceSubjectType(StrEnum):
    SKILL = "skill"
    PROJECT = "project"
    EXPERIENCE = "experience"
    EDUCATION = "education"
    CERTIFICATION = "certification"


class RequirementType(StrEnum):
    REQUIRED = "required"
    PREFERRED = "preferred"
    RESPONSIBILITY = "responsibility"
    DOMAIN_SIGNAL = "domain_signal"
    EDUCATION = "education"
    CERTIFICATION = "certification"


class AssessmentLevel(StrEnum):
    """Deliberately NOT a numeric score. See docs/domain-model.md §4."""

    STRONG = "strong"
    PARTIAL = "partial"
    WEAK = "weak"
    NONE = "none"
    CONFLICTING = "conflicting"


class ApplicationOutcomeType(StrEnum):
    NO_RESPONSE = "no_response"
    REJECTED = "rejected"
    INTERVIEW = "interview"
    OFFER = "offer"
    WITHDRAWN = "withdrawn"
