from pathlib import Path
import pytest
from playwright.sync_api import sync_playwright

from config.settings import TestSettings, load_settings
from utils.file_utils import ensure_dir, timestamp

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    if rep.when == "call" and rep.failed:
        page = item.funcargs.get("page")
        if page:
            import time, pathlib
            pathlib.Path("screenshots").mkdir(exist_ok=True)
            path = f"screenshots/FAILED_{item.name}_{int(time.time())}.png"
            try:
                page.screenshot(path=path, full_page=True)
                print(f"\n[FAILURE SCREENSHOT] {path}")
            except Exception as e:
                print(f"Could not capture failure screenshot: {e}")

@pytest.fixture(scope="session")
def settings() -> TestSettings:
    return load_settings()


@pytest.fixture()
def page(settings: TestSettings):
    ensure_dir(settings.project_root / "reports")
    ensure_dir(settings.project_root / "screenshots")
    ensure_dir(settings.project_root / "traces")
    ensure_dir(settings.project_root / "reports" / "videos")

    user_data_dir = settings.project_root / ".browser-profile"
    ensure_dir(user_data_dir)

    with sync_playwright() as playwright:
        context = playwright.chromium.launch_persistent_context(
            user_data_dir=str(user_data_dir),
            headless=settings.headless,
            slow_mo=settings.slow_mo_ms,
            locale="en-AU",
            viewport={"width": 1440, "height": 1000},
            record_video_dir=str(settings.project_root / "reports" / "videos"),
        )

        context.set_default_timeout(settings.default_timeout_ms)
        context.tracing.start(screenshots=True, snapshots=True, sources=True)

        test_page = context.pages[0] if context.pages else context.new_page()

        yield test_page

        trace_file = settings.project_root / "traces" / f"trace_{timestamp()}.zip"
        context.tracing.stop(path=str(trace_file))
        context.close()
