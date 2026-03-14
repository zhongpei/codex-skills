"""Ship workflow planning and safety gates."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ShipStep:
    name: str
    command: str
    requires_confirmation: bool = False


@dataclass(slots=True)
class ShipConfig:
    confirm_push_pr: bool = True


def bump_version(current: str, level: str) -> str:
    parts = [int(part) for part in current.split(".")]
    if len(parts) != 4:
        raise ValueError("version must be MAJOR.MINOR.PATCH.MICRO")

    if level == "micro":
        parts[3] += 1
    elif level == "patch":
        parts[2] += 1
        parts[3] = 0
    elif level == "minor":
        parts[1] += 1
        parts[2] = 0
        parts[3] = 0
    elif level == "major":
        parts[0] += 1
        parts[1] = 0
        parts[2] = 0
        parts[3] = 0
    else:
        raise ValueError(f"unsupported bump level: {level}")

    return ".".join(str(part) for part in parts)


def render_changelog_entry(version: str, date: str, bullets: list[str]) -> str:
    header = f"## {version} - {date}"
    body = "\n".join(f"- {line}" for line in bullets)
    return f"{header}\n\n{body}\n"


class ShipWorkflow:
    def __init__(self, config: ShipConfig | None = None) -> None:
        self.config = config or ShipConfig()

    def steps(self) -> list[ShipStep]:
        confirm = self.config.confirm_push_pr
        return [
            ShipStep("preflight-branch", "git branch --show-current"),
            ShipStep("preflight-status", "git status"),
            ShipStep("preflight-diff", "git diff origin/main...HEAD --stat"),
            ShipStep("merge-main", "git fetch origin main && git merge origin/main --no-edit"),
            ShipStep("tests", "uv run pytest"),
            ShipStep("review", "run review workflow"),
            ShipStep("version-bump", "update VERSION"),
            ShipStep("changelog", "update CHANGELOG.md"),
            ShipStep("commit", "git add -A && git commit -m 'chore: ship release'"),
            ShipStep("push", "git push", requires_confirmation=confirm),
            ShipStep("create-pr", "gh pr create --fill", requires_confirmation=confirm),
        ]

    def release_steps(self, include_pr: bool = True) -> list[str]:
        return [step.command for step in self.steps() if include_pr or step.name != "create-pr"]

    def confirmation_required(self, step_name: str) -> bool:
        for step in self.steps():
            if step.name == step_name:
                return step.requires_confirmation
        raise KeyError(step_name)
