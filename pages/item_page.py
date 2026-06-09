import random
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from pages.base_page import BasePage


class ItemPage(BasePage):
    """Product details page object for selecting variants and adding items to cart."""

    ADD_TO_CART_SELECTORS = [
        "#atcBtn_btn_1",
        "a#atcBtn_btn_1",
        "button#atcBtn_btn_1",
        "a:has-text('Add to cart')",
        "button:has-text('Add to cart')",
    ]

    def add_items_to_cart(self, urls: list[str]) -> None:
        for index, url in enumerate(urls, start=1):
            self.page.goto(url, wait_until="domcontentloaded")
            self.dismiss_known_popups()
            self._select_available_variants()
            self._add_current_item_to_cart(index)

    # CamelCase wrapper matching the exercise wording.
    def addItemsToCart(self, urls: list[str]) -> None:
        self.add_items_to_cart(urls)

    def _select_available_variants(self) -> None:
        """Choose random available dropdown values for size/color/etc. when present."""
        dropdowns = self.page.locator("select")
        for dropdown_index in range(dropdowns.count()):
            dropdown = dropdowns.nth(dropdown_index)
            try:
                if not dropdown.is_visible(timeout=1000):
                    continue

                options = dropdown.locator("option:not([disabled])")
                available_values: list[str] = []
                for option_index in range(options.count()):
                    option = options.nth(option_index)
                    value = option.get_attribute("value")
                    label = option.inner_text(timeout=500).strip().lower()
                    if value and value != "-1" and "select" not in label and "choose" not in label:
                        available_values.append(value)

                if available_values:
                    dropdown.select_option(random.choice(available_values))
            except Exception:
                continue

        # Some eBay variations are rendered as buttons or radio-like controls.
        variant_buttons = self.page.locator(
            "[role='radio']:not([aria-disabled='true']), "
            "button[aria-pressed='false']:not([disabled])"
        )
        for button_index in range(min(variant_buttons.count(), 3)):
            try:
                button = variant_buttons.nth(button_index)
                if button.is_visible(timeout=800):
                    button.click(timeout=1000)
            except Exception:
                continue

    def _add_current_item_to_cart(self, item_index: int) -> None:
        add_button = self.first_visible(self.ADD_TO_CART_SELECTORS, timeout=5000)
        if add_button is None:
            self.screenshot(f"item_{item_index}_add_button_not_found")
            raise AssertionError(f"Add to cart button was not found for item {item_index}.")

        try:
            add_button.click()
            self.page.wait_for_load_state("domcontentloaded")
            self.dismiss_known_popups()
            self.screenshot(f"item_{item_index}_added_to_cart")
        except PlaywrightTimeoutError as exc:
            self.screenshot(f"item_{item_index}_add_to_cart_timeout")
            raise AssertionError(f"Add to cart action timed out for item {item_index}.") from exc
