"""Common structures for skill workflows."""

from dataclasses import dataclass
from typing import Sequence


@dataclass(slots=True)
class SkillRunSummary:
    skill_name: str
    steps: Sequence[str]
    evidence_paths: Sequence[str]

    def to_markdown(self) -> str:
        step_lines = "\n".join(f"- {step}" for step in self.steps)
        evidence_lines = "\n".join(f"- {item}" for item in self.evidence_paths)
        return (
            f"## {self.skill_name}\n\n"
            f"### Steps\n{step_lines or '- (none)'}\n\n"
            f"### Evidence\n{evidence_lines or '- (none)'}"
        )
