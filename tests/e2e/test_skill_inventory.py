from pathlib import Path


SKILLS = [
    "plan-ceo-review",
    "plan-eng-review",
    "review",
    "ship",
    "browse",
    "qa",
    "setup-browser-cookies",
    "retro",
]


def test_all_skill_docs_exist() -> None:
    root = Path(__file__).resolve().parents[2]
    for skill in SKILLS:
        path = root / ".agents" / "skills" / skill / "SKILL.md"
        assert path.exists(), f"missing skill doc: {path}"


def test_supporting_templates_exist() -> None:
    root = Path(__file__).resolve().parents[2]
    assert (root / ".agents/skills/qa/templates/qa-report-template.md").exists()
    assert (root / ".agents/skills/review/checklist.md").exists()
    assert (root / ".agents/skills/review/greptile-triage.md").exists()
