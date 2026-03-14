"""Command-line entrypoint for gstack-codex helpers."""

from __future__ import annotations

import argparse
from datetime import UTC, datetime
from pathlib import Path

from .agent_browser import AgentBrowserCLI
from .errors import AgentBrowserError
from .skills.qa import HealthBreakdown, QAReport, write_report
from .skills.retro import parse_window
from .skills.ship import ShipWorkflow


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="gstack-codex")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("doctor", help="Validate agent-browser availability")

    browse_open = sub.add_parser("browse-open", help="Open a URL in agent-browser")
    browse_open.add_argument("url")

    save_state = sub.add_parser("save-state", help="Save browser auth state")
    save_state.add_argument("path")

    load_state = sub.add_parser("load-state", help="Load browser auth state")
    load_state.add_argument("path")

    qa_report = sub.add_parser("qa-report", help="Write a QA report skeleton to an output directory")
    qa_report.add_argument("--app", default="App")
    qa_report.add_argument("--url", required=True)
    qa_report.add_argument("--mode", default="full")
    qa_report.add_argument("--out", default=".gstack/qa-reports")

    ship_steps = sub.add_parser("ship-steps", help="Print ship step plan")
    ship_steps.add_argument("--no-pr", action="store_true")

    retro_window = sub.add_parser("retro-window", help="Validate and print parsed retro window")
    retro_window.add_argument("arg", nargs="*")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    cli = AgentBrowserCLI()

    try:
        if args.command == "doctor":
            cli.ensure_available()
            print("OK: agent-browser is available")
            return 0

        if args.command == "browse-open":
            result = cli.open(args.url)
            print(result.stdout)
            return result.returncode

        if args.command == "save-state":
            path = Path(args.path)
            path.parent.mkdir(parents=True, exist_ok=True)
            result = cli.state_save(str(path))
            print(result.stdout)
            return result.returncode

        if args.command == "load-state":
            result = cli.state_load(args.path)
            print(result.stdout)
            return result.returncode

        if args.command == "qa-report":
            report = QAReport(
                app_name=args.app,
                date=datetime.now(UTC).strftime("%Y-%m-%d"),
                url=args.url,
                mode=args.mode,
                duration="0m",
                pages_visited=1,
                screenshots=1,
                framework="Unknown",
                health=HealthBreakdown(),
                issues=[],
            )
            path = write_report(report, args.out)
            print(path)
            return 0

        if args.command == "ship-steps":
            workflow = ShipWorkflow()
            for command in workflow.release_steps(include_pr=not args.no_pr):
                print(command)
            return 0

        if args.command == "retro-window":
            raw = " ".join(args.arg).strip() if args.arg else None
            window = parse_window(raw if raw else None)
            print(f"raw={window.raw} amount={window.amount} unit={window.unit} compare={window.compare}")
            return 0

        parser.error(f"unsupported command: {args.command}")
    except (AgentBrowserError, ValueError) as exc:
        print(str(exc))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
