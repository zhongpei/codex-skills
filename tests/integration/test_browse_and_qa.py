from __future__ import annotations

from types import SimpleNamespace

from gstack_codex.skills.browse import BrowseWorkflow
from gstack_codex.skills.qa import QAMode, QAWorkflow, select_mode
from gstack_codex.skills.setup_browser_cookies import CookieSetupWorkflow


class FakeBrowser:
    def open(self, _url):
        return SimpleNamespace(stdout="opened")

    def snapshot(self, **_kwargs):
        return SimpleNamespace(stdout="snapshot")

    def console(self, **_kwargs):
        return SimpleNamespace(stdout="console")

    def errors(self, **_kwargs):
        return SimpleNamespace(stdout="errors")

    def screenshot(self, *_args, **_kwargs):
        return SimpleNamespace(stdout="screen")

    def network_requests(self, **_kwargs):
        return SimpleNamespace(stdout="net")

    def set_viewport(self, *_args, **_kwargs):
        return SimpleNamespace(stdout="viewport")

    def diff_url(self, *_args, **_kwargs):
        return SimpleNamespace(stdout="diff")

    def run(self, _args):
        return SimpleNamespace(stdout="run")

    def state_save(self, _path):
        return SimpleNamespace(stdout="saved")

    def cookies(self):
        return SimpleNamespace(stdout="cookies")

    def state_load(self, _path):
        return SimpleNamespace(stdout="loaded")


def test_browse_smoke_responsive_and_compare() -> None:
    workflow = BrowseWorkflow(FakeBrowser())
    smoke = workflow.smoke_check("https://example.com")
    assert smoke.snapshot == "snapshot"

    responsive = workflow.responsive_check("https://example.com", "/tmp/shot")
    assert responsive.desktop == "screen"

    diff = workflow.compare_urls("https://a", "https://b")
    assert diff == "diff"


def test_qa_modes_and_runs() -> None:
    assert select_mode(None, quick=True, regression=None, on_feature_branch=False) == QAMode.QUICK
    assert select_mode(None, quick=False, regression="baseline.json", on_feature_branch=False) == QAMode.REGRESSION
    assert select_mode("https://x", quick=False, regression=None, on_feature_branch=False) == QAMode.FULL
    assert select_mode(None, quick=False, regression=None, on_feature_branch=True) == QAMode.DIFF_AWARE

    workflow = QAWorkflow(FakeBrowser())
    quick = workflow.run_quick("https://example.com")
    assert len(quick) == 1

    full = workflow.run_full(["https://example.com", "https://example.com/about"])
    assert len(full) == 2

    diff_aware = workflow.run_diff_aware("https://example.com", ["app/controllers/users_controller.rb"])
    assert len(diff_aware) == 1

    reg = workflow.run_regression(90, "/tmp/non-existing-baseline.json")
    assert reg["baseline"] == 0


def test_cookie_workflow() -> None:
    workflow = CookieSetupWorkflow(FakeBrowser())
    saved = workflow.save_and_verify("states/a.json", "https://example.com")
    loaded = workflow.load_and_verify("states/a.json")
    assert saved.state_path.endswith("states/a.json")
    assert loaded.cookies_output == "cookies"
