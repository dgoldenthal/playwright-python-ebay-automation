from pathlib import Path
import pytest
from playwright.sync_api import sync_playwright
from config.settings import TestSettings, load_settings
from utils.file_utils import ensure_dir, timestamp


@pytest.fixture(scope="session")
def settings() -> TestSettings:
    return load_settings()


@pytest.fixture()
def page(settings: TestSettings):
    ensure_dir(settings.project_root / "reports")
    ensure_dir(settings.project_root / "screenshots")
    ensure_dir(settings.project_root / "traces")

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            headless=settings.headless,
            slow_mo=settings.slow_mo_ms,
        )
        context = browser.new_context(
            locale="en-AU",
            viewport={"width": 1440, "height": 1000},
            record_video_dir=str(settings.project_root / "reports" / "videos"),
        )
        context.tracing.start(screenshots=True, snapshots=True, sources=True)
        test_page = context.new_page()

        yield test_page

        trace_file = settings.project_root / "traces" / f"trace_{timestamp()}.zip"
        context.tracing.stop(path=str(trace_file))
        context.close()
        browser.close()
