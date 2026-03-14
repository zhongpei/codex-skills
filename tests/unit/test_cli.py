from __future__ import annotations

import types

import pytest

from gstack_codex import cli


class DummyBrowser:
    def ensure_available(self):
        return None

    def open(self, _url):
        return types.SimpleNamespace(stdout="opened", returncode=0)

    def state_save(self, _path):
        return types.SimpleNamespace(stdout="saved", returncode=0)

    def state_load(self, _path):
        return types.SimpleNamespace(stdout="loaded", returncode=0)


def run_main(monkeypatch: pytest.MonkeyPatch, argv: list[str]) -> int:
    monkeypatch.setattr("gstack_codex.cli.AgentBrowserCLI", lambda: DummyBrowser())
    monkeypatch.setattr("sys.argv", argv)
    return cli.main()


def test_doctor(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    code = run_main(monkeypatch, ["gstack-codex", "doctor"])
    out = capsys.readouterr().out
    assert code == 0
    assert "OK" in out


def test_browse_open(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    code = run_main(monkeypatch, ["gstack-codex", "browse-open", "https://example.com"])
    out = capsys.readouterr().out
    assert code == 0
    assert "opened" in out


def test_save_and_load_state(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], tmp_path) -> None:
    p = tmp_path / "states" / "dev.json"
    code_save = run_main(monkeypatch, ["gstack-codex", "save-state", str(p)])
    assert code_save == 0
    assert "saved" in capsys.readouterr().out

    code_load = run_main(monkeypatch, ["gstack-codex", "load-state", str(p)])
    assert code_load == 0
    assert "loaded" in capsys.readouterr().out


def test_qa_report_and_ship_steps(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], tmp_path) -> None:
    out_dir = tmp_path / "qa"
    code = run_main(
        monkeypatch,
        ["gstack-codex", "qa-report", "--app", "Demo", "--url", "https://example.com", "--out", str(out_dir)],
    )
    assert code == 0
    report_path = capsys.readouterr().out.strip()
    assert report_path.endswith("report.md")

    ship_code = run_main(monkeypatch, ["gstack-codex", "ship-steps"])
    ship_out = capsys.readouterr().out
    assert ship_code == 0
    assert "git push" in ship_out


def test_retro_window(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    code = run_main(monkeypatch, ["gstack-codex", "retro-window", "compare", "14d"])
    out = capsys.readouterr().out
    assert code == 0
    assert "compare=True" in out


def test_retro_window_invalid(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    code = run_main(monkeypatch, ["gstack-codex", "retro-window", "invalid"])
    out = capsys.readouterr().out
    assert code == 1
    assert "invalid retro window" in out
