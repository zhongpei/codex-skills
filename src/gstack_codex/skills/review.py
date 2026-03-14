"""Review workflow and Greptile triage helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


SEVERITIES = {"critical", "high", "medium", "low"}
VALID_GREPTILE = "VALID"
FIXED_GREPTILE = "FIXED"
FALSE_POSITIVE_GREPTILE = "FALSE_POSITIVE"
SUPPRESSED_GREPTILE = "SUPPRESSED"


@dataclass(slots=True)
class ReviewFinding:
    severity: str
    file: str
    detail: str
    fix: str


@dataclass(slots=True)
class GreptileComment:
    comment_id: int
    source: str
    path: str
    line: int | None
    body: str
    html_url: str


@dataclass(slots=True)
class GreptileClassification:
    comment: GreptileComment
    result: str
    rationale: str


def create_finding(severity: str, file: str, detail: str, fix: str = "") -> ReviewFinding:
    if severity not in SEVERITIES:
        raise ValueError(f"invalid severity: {severity}")
    if not file.strip():
        raise ValueError("file is required")
    if not detail.strip():
        raise ValueError("detail is required")
    return ReviewFinding(severity=severity, file=file, detail=detail, fix=fix.strip())


def review_commands(base_ref: str = "origin/main") -> list[str]:
    return [
        "git branch --show-current",
        f"git fetch origin main --quiet && git diff {base_ref} --stat",
        f"git diff {base_ref}",
    ]


def greptile_fetch_commands(repo_env: str = "$REPO", pr_env: str = "$PR_NUMBER") -> list[str]:
    return [
        f"gh api repos/{repo_env}/pulls/{pr_env}/comments --jq '.[] | select(.user.login == \"greptile-apps[bot]\")'",
        f"gh api repos/{repo_env}/issues/{pr_env}/comments --jq '.[] | select(.user.login == \"greptile-apps[bot]\")'",
    ]


def classify_comment(comment: GreptileComment, diff_text: str, suppressed_paths: Iterable[str]) -> GreptileClassification:
    if any(comment.path.startswith(prefix) for prefix in suppressed_paths):
        return GreptileClassification(comment=comment, result=SUPPRESSED_GREPTILE, rationale="suppressed by history")

    lower = comment.body.lower()
    if "already fixed" in lower or "fixed in" in lower:
        return GreptileClassification(comment=comment, result=FIXED_GREPTILE, rationale="comment body signals fixed state")

    location_hint = comment.path
    if comment.line is not None:
        location_hint = f"{location_hint}:{comment.line}"

    if location_hint in diff_text or comment.path in diff_text:
        return GreptileClassification(comment=comment, result=VALID_GREPTILE, rationale="comment maps to changed area")

    return GreptileClassification(comment=comment, result=FALSE_POSITIVE_GREPTILE, rationale="no matching context in diff")


def summary_line(classifications: Iterable[GreptileClassification]) -> str:
    counts = {
        VALID_GREPTILE: 0,
        FIXED_GREPTILE: 0,
        FALSE_POSITIVE_GREPTILE: 0,
        SUPPRESSED_GREPTILE: 0,
    }
    for item in classifications:
        counts[item.result] += 1
    total = sum(counts.values())
    return (
        f"+ {total} Greptile comments "
        f"({counts[VALID_GREPTILE]} valid, {counts[FIXED_GREPTILE]} fixed, {counts[FALSE_POSITIVE_GREPTILE]} fp)"
    )


def load_review_support_files(root: str) -> dict[str, Path]:
    base = Path(root)
    checklist = base / ".agents" / "skills" / "review" / "checklist.md"
    triage = base / ".agents" / "skills" / "review" / "greptile-triage.md"
    return {"checklist": checklist, "triage": triage}
