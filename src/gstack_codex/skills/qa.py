"""QA orchestration for quick/full/regression/diff-aware modes."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Iterable

from ..agent_browser import AgentBrowserCLI


class QAMode(str, Enum):
    QUICK = "quick"
    FULL = "full"
    REGRESSION = "regression"
    DIFF_AWARE = "diff-aware"


@dataclass(slots=True)
class QARequest:
    mode: QAMode
    url: str | None = None
    baseline: str | None = None
    scope: str = "Full app"


@dataclass(slots=True)
class HealthBreakdown:
    console: int = 100
    links: int = 100
    visual: int = 100
    functional: int = 100
    ux: int = 100
    performance: int = 100
    accessibility: int = 100

    def total(self) -> int:
        weights = {
            "console": 15,
            "links": 10,
            "visual": 20,
            "functional": 20,
            "ux": 15,
            "performance": 10,
            "accessibility": 10,
        }
        score = 0.0
        for key, weight in weights.items():
            score += getattr(self, key) * (weight / 100)
        return int(round(score))


@dataclass(slots=True)
class QAIssue:
    issue_id: str
    severity: str
    category: str
    url: str
    title: str
    description: str
    repro_steps: list[str]


@dataclass(slots=True)
class QAReport:
    app_name: str
    date: str
    url: str
    mode: str
    duration: str
    pages_visited: int
    screenshots: int
    framework: str
    health: HealthBreakdown
    issues: list[QAIssue] = field(default_factory=list)


def select_mode(url: str | None, quick: bool, regression: str | None, on_feature_branch: bool) -> QAMode:
    if quick:
        return QAMode.QUICK
    if regression:
        return QAMode.REGRESSION
    if url:
        return QAMode.FULL
    if on_feature_branch:
        return QAMode.DIFF_AWARE
    return QAMode.FULL


def infer_changed_routes(paths: Iterable[str]) -> list[str]:
    routes: set[str] = set()
    for raw in paths:
        path = raw.strip()
        if not path:
            continue
        if "routes" in path or "controller" in path:
            stem = Path(path).stem.replace("_controller", "")
            routes.add(f"/{stem}")
        elif "view" in path or "template" in path or "component" in path:
            parts = Path(path).parts
            if parts:
                routes.add(f"/{parts[-2]}")
        elif path.endswith((".md", ".html")):
            routes.add(f"/{Path(path).stem}")
    return sorted(routes)


def build_health_breakdown(
    *,
    console_errors: int,
    broken_links: int,
    functional_failures: int,
    visual_issues: int,
    ux_issues: int,
    perf_issues: int,
    a11y_issues: int,
) -> HealthBreakdown:
    def score(deductions: int, step: int = 10) -> int:
        return max(0, 100 - deductions * step)

    return HealthBreakdown(
        console=score(console_errors),
        links=score(broken_links),
        visual=score(visual_issues),
        functional=score(functional_failures),
        ux=score(ux_issues),
        performance=score(perf_issues),
        accessibility=score(a11y_issues),
    )


def render_report_markdown(report: QAReport) -> str:
    lines = [
        f"# QA Report: {report.app_name}",
        "",
        "| Field | Value |",
        "|-------|-------|",
        f"| **Date** | {report.date} |",
        f"| **URL** | {report.url} |",
        f"| **Scope** | Full app |",
        f"| **Mode** | {report.mode} |",
        f"| **Duration** | {report.duration} |",
        f"| **Pages visited** | {report.pages_visited} |",
        f"| **Screenshots** | {report.screenshots} |",
        f"| **Framework** | {report.framework} |",
        "",
        f"## Health Score: {report.health.total()}/100",
        "",
        "| Category | Score |",
        "|----------|-------|",
        f"| Console | {report.health.console} |",
        f"| Links | {report.health.links} |",
        f"| Visual | {report.health.visual} |",
        f"| Functional | {report.health.functional} |",
        f"| UX | {report.health.ux} |",
        f"| Performance | {report.health.performance} |",
        f"| Accessibility | {report.health.accessibility} |",
        "",
        "## Issues",
    ]

    if not report.issues:
        lines.append("\nNo issues found.")
    else:
        for issue in report.issues:
            lines.extend(
                [
                    "",
                    f"### {issue.issue_id}: {issue.title}",
                    "",
                    "| Field | Value |",
                    "|-------|-------|",
                    f"| **Severity** | {issue.severity} |",
                    f"| **Category** | {issue.category} |",
                    f"| **URL** | {issue.url} |",
                    "",
                    f"**Description:** {issue.description}",
                    "",
                    "**Repro Steps:**",
                ]
            )
            for index, step in enumerate(issue.repro_steps, start=1):
                lines.append(f"{index}. {step}")

    return "\n".join(lines).strip() + "\n"


def compute_regression_delta(current_score: int, baseline_score: int) -> dict[str, int]:
    return {
        "current": current_score,
        "baseline": baseline_score,
        "delta": current_score - baseline_score,
    }


class QAWorkflow:
    def __init__(self, browser: AgentBrowserCLI) -> None:
        self.browser = browser

    def _collect_page_evidence(self, url: str) -> dict[str, str]:
        self.browser.open(url)
        snap = self.browser.snapshot(interactive=True)
        screenshot = self.browser.screenshot(annotate=True)
        console = self.browser.console()
        errors = self.browser.errors()
        network = self.browser.network_requests()
        return {
            "url": url,
            "snapshot": snap.stdout,
            "screenshot": screenshot.stdout,
            "console": console.stdout,
            "errors": errors.stdout,
            "network": network.stdout,
        }

    def run_quick(self, url: str) -> list[dict[str, str]]:
        return [self._collect_page_evidence(url)]

    def run_full(self, urls: Iterable[str]) -> list[dict[str, str]]:
        return [self._collect_page_evidence(url) for url in urls]

    def run_diff_aware(self, base_url: str, changed_paths: Iterable[str]) -> list[dict[str, str]]:
        routes = infer_changed_routes(changed_paths)
        if not routes:
            return [self._collect_page_evidence(base_url)]
        return [self._collect_page_evidence(base_url.rstrip("/") + route) for route in routes]

    def run_regression(self, current_score: int, baseline_path: str) -> dict[str, int]:
        baseline_score = 0
        path = Path(baseline_path)
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            baseline_score = int(data.get("health_score", 0))
        return compute_regression_delta(current_score=current_score, baseline_score=baseline_score)


def write_report(report: QAReport, output_dir: str, name: str = "report.md") -> Path:
    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    report_path = root / name
    report_path.write_text(render_report_markdown(report), encoding="utf-8")

    baseline_path = root / "baseline.json"
    baseline_payload = {
        "generated_at": datetime.now(UTC).isoformat(),
        "health_score": report.health.total(),
        "issues": [issue.issue_id for issue in report.issues],
    }
    baseline_path.write_text(json.dumps(baseline_payload, indent=2), encoding="utf-8")
    return report_path
