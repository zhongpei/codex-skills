from gstack_codex.errors import AgentBrowserCommandError
from gstack_codex.models import BrowserResult


def test_browser_result_ok_property() -> None:
    assert BrowserResult(command=("x",), returncode=0, stdout="", stderr="").ok is True
    assert BrowserResult(command=("x",), returncode=1, stdout="", stderr="").ok is False


def test_command_error_str_contains_context() -> None:
    err = AgentBrowserCommandError(
        command=("agent-browser", "open", "x"),
        returncode=1,
        stdout="s",
        stderr="e",
    )
    msg = str(err)
    assert "agent-browser open x" in msg
    assert "code=1" in msg
