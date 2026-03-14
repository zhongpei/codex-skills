"""Cookie/session bootstrap flow with command-based parity."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ..agent_browser import AgentBrowserCLI


@dataclass(slots=True)
class CookieSetupResult:
    state_path: str
    cookies_output: str


def bootstrap_commands(state_path: str, target_url: str | None = None) -> list[str]:
    commands = [f"agent-browser --auto-connect state save {state_path}"]
    if target_url:
        commands.append(f"agent-browser --state {state_path} open {target_url}")
    commands.extend([f"agent-browser state load {state_path}", "agent-browser cookies"])
    return commands


class CookieSetupWorkflow:
    def __init__(self, browser: AgentBrowserCLI) -> None:
        self.browser = browser

    def save_and_verify(self, state_path: str, target_url: str | None = None) -> CookieSetupResult:
        path = Path(state_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        cmd_args = ["--auto-connect", "state", "save", str(path)]
        self.browser.run(cmd_args)
        if target_url:
            self.browser.run(("--state", str(path), "open", target_url))
        cookies_output = self.browser.cookies().stdout
        return CookieSetupResult(state_path=str(path), cookies_output=cookies_output)

    def load_and_verify(self, state_path: str) -> CookieSetupResult:
        self.browser.state_load(state_path)
        cookies_output = self.browser.cookies().stdout
        return CookieSetupResult(state_path=state_path, cookies_output=cookies_output)
