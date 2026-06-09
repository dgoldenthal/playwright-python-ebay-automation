from decimal import Decimal
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from pages.base_page import BasePage
from utils.price_parser import PriceParser


class SearchResultsPage(BasePage):
    """Search page object that returns item URLs whose price is under a maximum value."""

    SEARCH_INPUT_SELECTORS = ["#gh-ac", "input[name='_nkw']", "input[aria-label*='Search']"]
    SEARCH_BUTTON_SELECTORS = ["#gh-btn", "#gh-search-btn", "button[type='submit']"]
    MAX_PRICE_SELECTORS = [
        "input[name='_udhi']",
        "input[aria-label*='Maximum'][aria-label*='Value']",
        "input[aria-label*='Max']",
        "input.x-textrange__input--to",
    ]
    APPLY_PRICE_SELECTORS = [
        "button:has-text('Apply')",
        "button:has-text('Submit')",
        "button[aria-label*='Submit']",
    ]

    def search_items_by_name_under_price(
        self,
        query: str,
        max_price: int | float | Decimal,
        limit: int = 5,
    ) -> list[str]:
        self.open("")
        self._search(query)
        self._apply_max_price_filter(max_price)
        return self._collect_urls_under_price(Decimal(str(max_price)), limit)

    # CamelCase wrapper matching the exercise wording.
    def searchItemsByNameUnderPrice(
        self,
        query: str,
        maxPrice: int | float | Decimal,
        limit: int = 5,
    ) -> list[str]:
        return self.search_items_by_name_under_price(query, maxPrice, limit)

    def _search(self, query: str) -> None:
        search_input = self.first_visible(self.SEARCH_INPUT_SELECTORS)
        if search_input is None:
            raise AssertionError("Search input was not found.")

        search_input.fill(query)
        search_button = self.first_visible(self.SEARCH_BUTTON_SELECTORS, timeout=1500)
        if search_button:
            search_button.click()
        else:
            search_input.press("Enter")
        self.page.wait_for_load_state("domcontentloaded")
        self.dismiss_known_popups()

    def _apply_max_price_filter(self, max_price: int | float | Decimal) -> None:
        """Use site filter when visible. The final filtering is still done by parsed prices."""
        max_price_input = self.first_visible(self.MAX_PRICE_SELECTORS, timeout=2000)
        if max_price_input is None:
            return

        try:
            max_price_input.fill(str(max_price))
            apply_button = self.first_visible(self.APPLY_PRICE_SELECTORS, timeout=1200)
            if apply_button:
                apply_button.click()
            else:
                max_price_input.press("Enter")
            self.page.wait_for_load_state("domcontentloaded")
        except Exception:
            # Do not fail here. Price validation below is the source of truth.
            return

    def _collect_urls_under_price(self, max_price: Decimal, limit: int) -> list[str]:
        urls: list[str] = []
        seen_urls: set[str] = set()

        while len(urls) < limit:
            self.page.wait_for_load_state("domcontentloaded")
            # XPath is intentionally used because the exercise requests XPath extraction.
            result_cards = self.page.locator(
                "xpath=//li[contains(@class,'s-item') and .//a[contains(@class,'s-item__link')]]"
            )

            for index in range(result_cards.count()):
                if len(urls) >= limit:
                    break

                card = result_cards.nth(index)
                url = self._extract_item_url(card)
                price = self._extract_item_price(card)

                if not url or url in seen_urls or price is None:
                    continue

                if price <= max_price:
                    urls.append(url)
                    seen_urls.add(url)

            if len(urls) >= limit or not self._go_to_next_results_page():
                break

        return urls

    def _extract_item_url(self, card) -> str | None:
        try:
            href = card.locator("a.s-item__link").first.get_attribute("href", timeout=2000)
            if not href:
                return None
            return href.split("?")[0]
        except Exception:
            return None

    def _extract_item_price(self, card) -> Decimal | None:
        price_selectors = [".s-item__price", "span:has-text('$')"]
        for selector in price_selectors:
            try:
                price_text = card.locator(selector).first.inner_text(timeout=1200)
                price = PriceParser.lowest_price(price_text)
                if price is not None:
                    return price
            except Exception:
                continue
        return None

    def _go_to_next_results_page(self) -> bool:
        next_selectors = [
            "a.pagination__next:not([aria-disabled='true'])",
            "a[aria-label*='next page' i]",
            "a:has-text('Next')",
        ]
        next_button = self.first_visible(next_selectors, timeout=2000)
        if next_button is None:
            return False

        try:
            next_button.click()
            self.page.wait_for_load_state("domcontentloaded")
            return True
        except PlaywrightTimeoutError:
            return False
