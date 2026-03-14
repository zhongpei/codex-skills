from __future__ import annotations

import json
from pathlib import Path

import pytest

from gstack_codex.skills.browse import translate_legacy_command
from gstack_codex.skills.common import SkillRunSummary
from gstack_codex.skills.plan_ceo_review import build_scope_review, required_sections as ceo_sections
from gstack_codex.skills.plan_eng_review import default_checklist, required_sections as eng_sections
from gstack_codex.skills.qa import (
    HealthBreakdown,
    QAReport,
    build_health_breakdown,
    compute_regression_delta,
    infer_changed_routes,
    render_report_markdown,
    write_report,
)
from gstack_codex.skills.review import (
    FALSE_POSITIVE_GREPTILE,
    FIXED_GREPTILE,
    SUPPRESSED_GREPTILE,
    VALID_GREPTILE,
    GreptileComment,
    classify_comment,
    create_finding,
    greptile_fetch_commands,
    load_review_support_files,
    review_commands,
    summary_line,
)
from gstack_codex.skills.retro import (
    RetroSummary,
    compare_scores,
    health_signal,
    load_latest_snapshot,
    parse_window,
    retro_commands,
    write_snapshot,
)
from gstack_codex.skills.setup_browser_cookies import bootstrap_commands
from gstack_codex.skills.ship import ShipWorkflow, bump_version, render_changelog_entry


def test_skill_run_summary_markdown() -> None:
    summary = SkillRunSummary("qa", ["open", "snapshot"], ["/tmp/a.png"])
    md = summary.to_markdown()
    assert "## qa" in md
    assert "/tmp/a.png" in md


def test_plan_sections_and_validation() -> None:
    review = build_scope_review("hold_scope", ["A", " ", "B"])
    assert review.challenges == ["A", "B"]
    assert "Step 0: Nuclear Scope Challenge + Mode Selection" in ceo_sections()
    assert "Step 0: Scope Challenge" in eng_sections()

    checklist = default_checklist()
    assert checklist.architecture is True

    with pytest.raises(ValueError):
        build_scope_review("bad", ["A"])


def test_review_helpers(tmp_path: Path) -> None:
    finding = create_finding("high", "x.py", "issue", "fix")
    assert finding.fix == "fix"

    commands = review_commands()
    assert commands[0].startswith("git branch")
    assert "pulls" in greptile_fetch_commands()[0]

    comment = GreptileComment(1, "line-level", "app/a.py", 10, "looks wrong", "http://x")
    cls_valid = classify_comment(comment, "app/a.py:10", [])
    assert cls_valid.result == VALID_GREPTILE

    cls_supp = classify_comment(comment, "", ["app/"])
    assert cls_supp.result == SUPPRESSED_GREPTILE

    fixed_comment = GreptileComment(2, "line-level", "app/b.py", 5, "already fixed in abc", "http://y")
    cls_fixed = classify_comment(fixed_comment, "", [])
    assert cls_fixed.result == FIXED_GREPTILE

    fp_comment = GreptileComment(3, "top-level", "lib/x.py", None, "noise", "http://z")
    cls_fp = classify_comment(fp_comment, "", [])
    assert cls_fp.result == FALSE_POSITIVE_GREPTILE

    summary = summary_line([cls_valid, cls_supp, cls_fixed, cls_fp])
    assert "Greptile comments" in summary

    root = tmp_path / "repo"
    (root / ".agents/skills/review").mkdir(parents=True)
    files = load_review_support_files(str(root))
    assert files["checklist"].name == "checklist.md"

    with pytest.raises(ValueError):
        create_finding("bad", "x.py", "issue")


def test_ship_helpers() -> None:
    assert bump_version("1.2.3.4", "micro") == "1.2.3.5"
    assert bump_version("1.2.3.4", "patch") == "1.2.4.0"
    assert bump_version("1.2.3.4", "minor") == "1.3.0.0"
    assert bump_version("1.2.3.4", "major") == "2.0.0.0"

    with pytest.raises(ValueError):
        bump_version("1.2.3", "micro")
    with pytest.raises(ValueError):
        bump_version("1.2.3.4", "bad")

    entry = render_changelog_entry("1.2.3.5", "2026-03-14", ["Fix A", "Fix B"])
    assert "## 1.2.3.5 - 2026-03-14" in entry

    workflow = ShipWorkflow()
    steps = workflow.steps()
    assert any(step.name == "push" and step.requires_confirmation for step in steps)
    assert workflow.confirmation_required("push") is True

    with pytest.raises(KeyError):
        workflow.confirmation_required("unknown")


def test_qa_helpers(tmp_path: Path) -> None:
    routes = infer_changed_routes(["app/controllers/users_controller.rb", "app/views/orders/show.html.erb", "docs/intro.md"])
    assert "/users" in routes

    breakdown = build_health_breakdown(
        console_errors=1,
        broken_links=2,
        functional_failures=0,
        visual_issues=1,
        ux_issues=0,
        perf_issues=0,
        a11y_issues=0,
    )
    assert 0 <= breakdown.total() <= 100

    report = QAReport(
        app_name="Demo",
        date="2026-03-14",
        url="https://example.com",
        mode="full",
        duration="2m",
        pages_visited=3,
        screenshots=3,
        framework="Unknown",
        health=HealthBreakdown(),
    )
    md = render_report_markdown(report)
    assert "# QA Report: Demo" in md

    out = write_report(report, str(tmp_path))
    assert out.exists()
    baseline = json.loads((tmp_path / "baseline.json").read_text(encoding="utf-8"))
    assert baseline["health_score"] == 100

    delta = compute_regression_delta(80, 70)
    assert delta["delta"] == 10


def test_retro_helpers(tmp_path: Path) -> None:
    default_window = parse_window(None)
    compare_window = parse_window("compare 14d")
    assert default_window.raw == "7d"
    assert compare_window.compare is True

    with pytest.raises(ValueError):
        parse_window("oops")

    commands = retro_commands(compare_window)
    assert commands[0].startswith("git fetch")

    current = RetroSummary(5, 2, 1000, 200)
    previous = RetroSummary(3, 2, 500, 100)
    assert compare_scores(current, previous)["commit_delta"] == 2
    assert health_signal(current) == "steady"

    snapshot = write_snapshot(current, directory=str(tmp_path / "retros"))
    assert snapshot.exists()
    latest = load_latest_snapshot(directory=str(tmp_path / "retros"))
    assert latest is not None
    assert latest.commits == 5


def test_browse_and_cookie_small_helpers() -> None:
    assert translate_legacy_command("goto") == "open"
    assert translate_legacy_command("unknown") == "unknown"
    cmds = bootstrap_commands("./states/a.json", "https://example.com")
    assert cmds[0].startswith("agent-browser --auto-connect")
