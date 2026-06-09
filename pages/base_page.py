from pathlib import Path
from playwright.sync_api import Page, Locator, TimeoutError as PlaywrightTimeoutError
from config.settings import TestSettings
from utils.file_utils import ensure_dir, safe_filename, timestamp


class BasePage:
    """Base class shared by all page objects."""

    def __init__(self, page: Page, settings: TestSettings):
        self.page = page
        self.settings = settings
        self.page.set_default_timeout(settings.default_timeout_ms)

    def open(self, path: str = "") -> None:
        url = f"{self.settings.base_url}/{path.lstrip('/')}"
        self.page.goto(url, wait_until="domcontentloaded")
        self.dismiss_known_popups()

    def dismiss_known_popups(self) -> None:
        """Best-effort handling for consent/sign-up popups without failing the test."""
        candidates = [
            "button:has-text('Accept all')",
            "button:has-text('Accept')",
            "button:has-text('Agree')",
            "button:has-text('Got it')",
            "button[aria-label='Close']",
            "button:has-text('No thanks')",
        ]
        for selector in candidates:
            try:
                locator = self.page.locator(selector).first
                if locator.is_visible(timeout=800):
                    locator.click(timeout=1500)
            except PlaywrightTimeoutError:
                continue
            except Exception:
                continue

    def first_visible(self, selectors: list[str], timeout: int = 3000) -> Locator | None:
        for selector in selectors:
            try:
                locator = self.page.locator(selector).first
                if locator.is_visible(timeout=timeout):
                    return locator
            except Exception:
                continue
        return None

    def screenshot(self, name: str) -> Path:
        screenshots_dir = ensure_dir(self.settings.project_root / "screenshots")
        file_path = screenshots_dir / f"{timestamp()}_{safe_filename(name)}.png"
        self.page.screenshot(path=str(file_path), full_page=True)
        return file_path
