"""Retro workflow helpers with compare-mode and snapshot persistence."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path


@dataclass(slots=True)
class RetroWindow:
    raw: str
    amount: int
    unit: str
    compare: bool = False


@dataclass(slots=True)
class RetroSummary:
    commits: int
    contributors: int
    insertions: int
    deletions: int

    @property
    def net(self) -> int:
        return self.insertions - self.deletions


def parse_window(arg: str | None) -> RetroWindow:
    if not arg:
        return RetroWindow(raw="7d", amount=7, unit="d", compare=False)

    tokens = arg.split()
    compare = tokens[0] == "compare"
    raw = tokens[-1] if compare and len(tokens) > 1 else ("7d" if compare else tokens[0])

    if len(raw) < 2 or raw[-1] not in {"d", "h", "w"} or not raw[:-1].isdigit():
        raise ValueError("invalid retro window")

    return RetroWindow(raw=raw, amount=int(raw[:-1]), unit=raw[-1], compare=compare)


def retro_commands(window: RetroWindow) -> list[str]:
    since_map = {"d": "days", "h": "hours", "w": "weeks"}
    since = f"{window.amount} {since_map[window.unit]} ago"
    return [
        "git fetch origin main --quiet",
        "git config user.name",
        "git config user.email",
        f"git log origin/main --since=\"{since}\" --format=\"%H|%aN|%ae|%ai|%s\" --shortstat",
        f"git shortlog origin/main --since=\"{since}\" -sn --no-merges",
    ]


def health_signal(summary: RetroSummary) -> str:
    if summary.commits == 0:
        return "no-activity"
    if summary.net < 0:
        return "stabilization"
    if summary.net > 1500:
        return "high-change"
    return "steady"


def compare_scores(current: RetroSummary, previous: RetroSummary) -> dict[str, int]:
    return {
        "commit_delta": current.commits - previous.commits,
        "net_delta": current.net - previous.net,
    }


def write_snapshot(summary: RetroSummary, directory: str = ".context/retros") -> Path:
    root = Path(directory)
    root.mkdir(parents=True, exist_ok=True)
    today = date.today().isoformat()
    existing = sorted(root.glob(f"{today}-*.json"))
    next_index = len(existing) + 1
    out = root / f"{today}-{next_index}.json"
    out.write_text(json.dumps(asdict(summary), indent=2), encoding="utf-8")
    return out


def load_latest_snapshot(directory: str = ".context/retros") -> RetroSummary | None:
    root = Path(directory)
    if not root.exists():
        return None
    files = sorted(root.glob("*.json"))
    if not files:
        return None
    data = json.loads(files[-1].read_text(encoding="utf-8"))
    return RetroSummary(**data)
