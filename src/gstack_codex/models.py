"""Data models used by gstack-codex core modules."""

from dataclasses import dataclass


@dataclass(slots=True)
class BrowserResult:
    """Structured command output from agent-browser."""

    command: tuple[str, ...]
    returncode: int
    stdout: str
    stderr: str

    @property
    def ok(self) -> bool:
        return self.returncode == 0
