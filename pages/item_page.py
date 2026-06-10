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

    def add_items_to_cart(self, urls: list[str], return_url: str | None = None) -> None:
        """Open each product URL, select required variants, add it to cart, and return to search.

        Args:
            urls: Product detail-page URLs returned by the search page.
            return_url: Optional search-results URL. If omitted, the current page URL is used.

        The exercise asks the flow to return to the search screen/tab after each item. The
        implementation uses the same browser tab and navigates back to the saved search URL after
        every add-to-cart operation.
        """
        if not urls:
            return

        search_screen_url = return_url or self.page.url

        for index, url in enumerate(urls, start=1):
            self.page.goto(url, wait_until="domcontentloaded")
            self.dismiss_known_popups()
            self._select_available_variants()
            self._add_current_item_to_cart(index)
            self._return_to_search_screen(search_screen_url, index)

    # CamelCase wrapper matching the exercise wording.
    def addItemsToCart(self, urls: list[str]) -> None:
        self.add_items_to_cart(urls)

    def _select_available_variants(self) -> None:
        """Choose random available size/color/quantity variants when required."""
        self._select_dropdown_variants()
        self._select_button_or_radio_variants()

    def _select_dropdown_variants(self) -> None:
        dropdowns = self.page.locator("select")

        for dropdown_index in range(dropdowns.count()):
            dropdown = dropdowns.nth(dropdown_index)
            try:
                if not dropdown.is_visible(timeout=1000) or not dropdown.is_enabled(timeout=1000):
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

    def _select_button_or_radio_variants(self) -> None:
        """Randomly select visible enabled button/radio-style variants.

        Some eBay pages render variants as buttons or radio controls rather than dropdowns. The
        selectors below are intentionally broad because live eBay markup varies between products.
        """
        selectors = [
            "[role='radio'][aria-checked='false']:not([aria-disabled='true'])",
            "[role='radio']:not([aria-disabled='true'])",
            "button[aria-pressed='false']:not([disabled])",
            "input[type='radio']:not([disabled])",
        ]

        candidates = []
        for selector in selectors:
            controls = self.page.locator(selector)
            try:
                count = min(controls.count(), 30)
            except Exception:
                continue

            for control_index in range(count):
                control = controls.nth(control_index)
                try:
                    if control.is_visible(timeout=500) and control.is_enabled(timeout=500):
                        candidates.append(control)
                except Exception:
                    continue

        random.shuffle(candidates)

        # Select only a few candidate controls. This avoids clicking too many unrelated page buttons.
        selections_made = 0
        for control in candidates:
            if selections_made >= 3:
                break
            try:
                control.click(timeout=1200)
                selections_made += 1
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

    def _return_to_search_screen(self, search_screen_url: str, item_index: int) -> None:
        if not search_screen_url:
            return

        try:
            self.page.goto(search_screen_url, wait_until="domcontentloaded")
            self.dismiss_known_popups()
        except PlaywrightTimeoutError as exc:
            self.screenshot(f"item_{item_index}_return_to_search_timeout")
            raise AssertionError(f"Could not return to the search screen after item {item_index}.") from exc
