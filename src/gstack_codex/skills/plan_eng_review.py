"""Planning support for engineering review mode."""

from dataclasses import dataclass


@dataclass(slots=True)
class EngineeringReviewChecklist:
    architecture: bool
    failure_modes: bool
    test_matrix: bool
    observability: bool


REQUIRED_SECTIONS = [
    "Step 0: Scope Challenge",
    "Architecture review",
    "Code quality review",
    "Test review",
    "Performance review",
    "Completion summary",
]


def default_checklist() -> EngineeringReviewChecklist:
    return EngineeringReviewChecklist(
        architecture=True,
        failure_modes=True,
        test_matrix=True,
        observability=True,
    )


def required_sections() -> list[str]:
    return list(REQUIRED_SECTIONS)
