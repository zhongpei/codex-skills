"""Browse workflows with legacy-command mapping onto agent-browser."""

from __future__ import annotations

from dataclasses import dataclass

from ..agent_browser import AgentBrowserCLI


LEGACY_TO_AGENT_BROWSER = {
    "goto": "open",
    "snapshot": "snapshot",
    "click": "click",
    "fill": "fill",
    "console": "console",
    "network": "network requests",
    "screenshot": "screenshot",
    "responsive": "set viewport + screenshot matrix",
    "dialog-accept": "dialog accept",
    "dialog-dismiss": "dialog dismiss",
    "diff": "diff url",
}


@dataclass(slots=True)
class BrowseWorkflowResult:
    snapshot: str
    console: str
    errors: str


@dataclass(slots=True)
class ResponsiveArtifact:
    mobile: str
    tablet: str
    desktop: str


def translate_legacy_command(command: str) -> str:
    return LEGACY_TO_AGENT_BROWSER.get(command, command)


class BrowseWorkflow:
    def __init__(self, browser: AgentBrowserCLI) -> None:
        self.browser = browser

    def smoke_check(self, url: str) -> BrowseWorkflowResult:
        self.browser.open(url)
        snapshot = self.browser.snapshot(interactive=True).stdout
        console = self.browser.console().stdout
        errors = self.browser.errors().stdout
        return BrowseWorkflowResult(snapshot=snapshot, console=console, errors=errors)

    def responsive_check(self, url: str, prefix: str) -> ResponsiveArtifact:
        self.browser.open(url)
        self.browser.set_viewport(375, 812)
        mobile = self.browser.screenshot(f"{prefix}-mobile.png").stdout
        self.browser.set_viewport(768, 1024)
        tablet = self.browser.screenshot(f"{prefix}-tablet.png").stdout
        self.browser.set_viewport(1280, 720)
        desktop = self.browser.screenshot(f"{prefix}-desktop.png").stdout
        return ResponsiveArtifact(mobile=mobile, tablet=tablet, desktop=desktop)

    def compare_urls(self, left_url: str, right_url: str) -> str:
        return self.browser.diff_url(left_url, right_url, screenshot=True).stdout
