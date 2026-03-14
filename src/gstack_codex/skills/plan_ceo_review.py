"""Planning support for product/CEO review mode."""

from dataclasses import dataclass
from typing import Iterable


@dataclass(slots=True)
class ScopeReview:
    mode: str
    challenges: list[str]


VALID_MODES = {"scope_expansion", "hold_scope", "scope_reduction"}


REQUIRED_SECTIONS = [
    "Step 0: Nuclear Scope Challenge + Mode Selection",
    "Architecture Review",
    "Error & Rescue Map",
    "Security & Threat Model",
    "Failure Modes Registry",
    "Completion Summary",
]


def build_scope_review(mode: str, prompts: Iterable[str]) -> ScopeReview:
    if mode not in VALID_MODES:
        raise ValueError(f"unsupported mode: {mode}")
    items = [p.strip() for p in prompts if p.strip()]
    if not items:
        raise ValueError("at least one prompt is required")
    return ScopeReview(mode=mode, challenges=items)


def required_sections() -> list[str]:
    return list(REQUIRED_SECTIONS)
