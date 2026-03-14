"""Direct command runner for the `agent-browser` CLI."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from typing import Mapping, Sequence

from .errors import AgentBrowserCommandError, AgentBrowserUnavailableError
from .models import BrowserResult


class AgentBrowserCLI:
    """Small helper around direct `agent-browser` command execution."""

    def __init__(
        self,
        binary: str = "agent-browser",
        default_args: Sequence[str] | None = None,
        env: Mapping[str, str] | None = None,
        timeout_seconds: int = 60,
    ) -> None:
        self.binary = binary
        self.default_args = tuple(default_args or ())
        self.env = dict(env or {})
        self.timeout_seconds = timeout_seconds

    def is_available(self) -> bool:
        return shutil.which(self.binary) is not None

    def ensure_available(self) -> None:
        if not self.is_available():
            raise AgentBrowserUnavailableError(
                f"`{self.binary}` was not found. Install with `npm install -g agent-browser` "
                "then run `agent-browser install`."
            )

    def run(
        self,
        args: Sequence[str],
        *,
        check: bool = True,
        timeout_seconds: int | None = None,
        cwd: str | Path | None = None,
        env: Mapping[str, str] | None = None,
    ) -> BrowserResult:
        self.ensure_available()
        cmd = (self.binary, *self.default_args, *tuple(args))
        merged_env = os.environ.copy()
        merged_env.update(self.env)
        if env:
            merged_env.update(env)

        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout_seconds or self.timeout_seconds,
            cwd=cwd,
            env=merged_env,
        )
        result = BrowserResult(
            command=cmd,
            returncode=proc.returncode,
            stdout=proc.stdout.strip(),
            stderr=proc.stderr.strip(),
        )
        if check and not result.ok:
            raise AgentBrowserCommandError(
                command=result.command,
                returncode=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
            )
        return result

    def run_command(self, *args: str, check: bool = True) -> BrowserResult:
        return self.run(args, check=check)

    def open(self, url: str) -> BrowserResult:
        return self.run(("open", url))

    def snapshot(self, *, interactive: bool = False, compact: bool = False, diff: bool = False) -> BrowserResult:
        args = ["snapshot"]
        if interactive:
            args.append("--interactive")
        if compact:
            args.append("--compact")
        if diff:
            args.extend(["--diff"])
        return self.run(args)

    def click(self, selector: str) -> BrowserResult:
        return self.run(("click", selector))

    def fill(self, selector: str, value: str) -> BrowserResult:
        return self.run(("fill", selector, value))

    def hover(self, selector: str) -> BrowserResult:
        return self.run(("hover", selector))

    def press(self, key: str) -> BrowserResult:
        return self.run(("press", key))

    def upload(self, selector: str, files: Sequence[str]) -> BrowserResult:
        return self.run(("upload", selector, *files))

    def wait(
        self,
        target: str | None = None,
        *,
        text: str | None = None,
        url_pattern: str | None = None,
        load: str | None = None,
        state: str | None = None,
    ) -> BrowserResult:
        args = ["wait"]
        if target:
            args.append(target)
        if text:
            args.extend(["--text", text])
        if url_pattern:
            args.extend(["--url", url_pattern])
        if load:
            args.extend(["--load", load])
        if state:
            args.extend(["--state", state])
        return self.run(args)

    def screenshot(
        self,
        path: str | None = None,
        *,
        annotate: bool = False,
        full: bool = False,
    ) -> BrowserResult:
        args = ["screenshot"]
        if path:
            args.append(path)
        if annotate:
            args.append("--annotate")
        if full:
            args.append("--full")
        return self.run(args)

    def diff_url(
        self,
        left_url: str,
        right_url: str,
        *,
        screenshot: bool = False,
        selector: str | None = None,
    ) -> BrowserResult:
        args = ["diff", "url", left_url, right_url]
        if screenshot:
            args.append("--screenshot")
        if selector:
            args.extend(["--selector", selector])
        return self.run(args)

    def console(self, *, clear: bool = False) -> BrowserResult:
        args = ["console"]
        if clear:
            args.append("--clear")
        return self.run(args)

    def errors(self, *, clear: bool = False) -> BrowserResult:
        args = ["errors"]
        if clear:
            args.append("--clear")
        return self.run(args)

    def network_requests(self, *, filter_text: str | None = None) -> BrowserResult:
        args = ["network", "requests"]
        if filter_text:
            args.extend(["--filter", filter_text])
        return self.run(args)

    def set_viewport(self, width: int, height: int, scale: int | None = None) -> BrowserResult:
        args: list[str] = ["set", "viewport", str(width), str(height)]
        if scale is not None:
            args.append(str(scale))
        return self.run(args)

    def dialog_accept(self, text: str | None = None) -> BrowserResult:
        args = ["dialog", "accept"]
        if text:
            args.append(text)
        return self.run(args)

    def dialog_dismiss(self) -> BrowserResult:
        return self.run(("dialog", "dismiss"))

    def tab_list(self) -> BrowserResult:
        return self.run(("tab",))

    def tab_new(self, url: str | None = None) -> BrowserResult:
        args = ["tab", "new"]
        if url:
            args.append(url)
        return self.run(args)

    def tab_switch(self, index: int) -> BrowserResult:
        return self.run(("tab", str(index)))

    def state_save(self, path: str) -> BrowserResult:
        return self.run(("state", "save", path))

    def state_load(self, path: str) -> BrowserResult:
        return self.run(("state", "load", path))

    def cookies(self) -> BrowserResult:
        return self.run(("cookies",))

    def cookies_set(self, name: str, value: str) -> BrowserResult:
        return self.run(("cookies", "set", name, value))

    def cookies_clear(self) -> BrowserResult:
        return self.run(("cookies", "clear"))
