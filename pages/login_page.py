from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from pages.base_page import BasePage


class LoginPage(BasePage):
    """Authentication page object.

    eBay often requires MFA/CAPTCHA. For this exercise, the default flow is guest mode.
    If credentials are supplied through environment variables, the class attempts sign-in.
    """

    def authenticate(self) -> str:
        if not self.settings.username or not self.settings.password:
            self.open("")
            return "guest"

        self.open("signin")
        try:
            self.page.locator("#userid, input[name='userid']").first.fill(self.settings.username)
            self.page.locator("#signin-continue-btn, button:has-text('Continue')").first.click()
            self.page.locator("#pass, input[name='pass']").first.fill(self.settings.password)
            self.page.locator("#sgnBt, button:has-text('Sign in')").first.click()
            self.page.wait_for_load_state("domcontentloaded")
        except PlaywrightTimeoutError as exc:
            self.screenshot("login_failed")
            raise AssertionError("Login did not complete. eBay may require MFA/CAPTCHA.") from exc

        return "authenticated"
