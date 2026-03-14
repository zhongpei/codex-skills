"""Custom exceptions for gstack-codex."""

from dataclasses import dataclass


class AgentBrowserError(RuntimeError):
    """Base error for agent-browser interaction failures."""


class AgentBrowserUnavailableError(AgentBrowserError):
    """Raised when agent-browser binary is missing."""


@dataclass(slots=True)
class AgentBrowserCommandError(AgentBrowserError):
    """Raised when an agent-browser command fails."""

    command: tuple[str, ...]
    returncode: int
    stdout: str
    stderr: str

    def __str__(self) -> str:
        cmd = " ".join(self.command)
        return (
            f"agent-browser command failed (code={self.returncode}): {cmd}\n"
            f"stdout:\n{self.stdout}\n"
            f"stderr:\n{self.stderr}"
        )
