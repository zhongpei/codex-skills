from __future__ import annotations

import subprocess

import pytest

from gstack_codex.agent_browser import AgentBrowserCLI
from gstack_codex.errors import AgentBrowserCommandError, AgentBrowserUnavailableError


def test_is_available_true(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("gstack_codex.agent_browser.shutil.which", lambda _: "/usr/bin/agent-browser")
    assert AgentBrowserCLI().is_available() is True


def test_is_available_false(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("gstack_codex.agent_browser.shutil.which", lambda _: None)
    assert AgentBrowserCLI().is_available() is False


def test_ensure_available_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("gstack_codex.agent_browser.shutil.which", lambda _: None)
    with pytest.raises(AgentBrowserUnavailableError):
        AgentBrowserCLI().ensure_available()


def test_run_success(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("gstack_codex.agent_browser.shutil.which", lambda _: "/usr/bin/agent-browser")

    def fake_run(*_args, **_kwargs):
        return subprocess.CompletedProcess(args=[], returncode=0, stdout="ok\n", stderr="")

    monkeypatch.setattr("gstack_codex.agent_browser.subprocess.run", fake_run)
    cli = AgentBrowserCLI(default_args=("--session", "test"))
    res = cli.run(("open", "https://example.com"))
    assert res.ok is True
    assert res.stdout == "ok"
    assert res.command[:3] == ("agent-browser", "--session", "test")


def test_run_failure_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("gstack_codex.agent_browser.shutil.which", lambda _: "/usr/bin/agent-browser")

    def fake_run(*_args, **_kwargs):
        return subprocess.CompletedProcess(args=[], returncode=2, stdout="", stderr="bad")

    monkeypatch.setattr("gstack_codex.agent_browser.subprocess.run", fake_run)
    with pytest.raises(AgentBrowserCommandError):
        AgentBrowserCLI().run(("open", "bad://url"))


def test_command_helpers(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("gstack_codex.agent_browser.shutil.which", lambda _: "/usr/bin/agent-browser")

    called: list[tuple[str, ...]] = []

    def fake_run(self, args, **_kwargs):
        called.append(tuple(args))
        return type("R", (), {"stdout": "x", "returncode": 0, "ok": True})()

    monkeypatch.setattr("gstack_codex.agent_browser.AgentBrowserCLI.run", fake_run)

    cli = AgentBrowserCLI()
    cli.open("https://example.com")
    cli.run_command("open", "https://example.com")
    cli.snapshot(interactive=True, compact=True, diff=True)
    cli.click("@e1")
    cli.fill("@e2", "v")
    cli.hover("@e3")
    cli.press("Enter")
    cli.upload("#file", ["a.txt"])
    cli.wait("#ready", text="ok", url_pattern="**/ok", load="networkidle", state="visible")
    cli.screenshot("a.png", annotate=True, full=True)
    cli.diff_url("https://a", "https://b", screenshot=True, selector="#app")
    cli.console(clear=True)
    cli.errors(clear=True)
    cli.network_requests(filter_text="api")
    cli.set_viewport(375, 812, 2)
    cli.dialog_accept("yes")
    cli.dialog_dismiss()
    cli.tab_list()
    cli.tab_new("https://x")
    cli.tab_switch(1)
    cli.state_save("state.json")
    cli.state_load("state.json")
    cli.cookies()
    cli.cookies_set("k", "v")
    cli.cookies_clear()

    assert ("snapshot", "--interactive", "--compact", "--diff") in called
    assert ("diff", "url", "https://a", "https://b", "--screenshot", "--selector", "#app") in called
    assert ("set", "viewport", "375", "812", "2") in called
    assert ("cookies", "clear") in called
