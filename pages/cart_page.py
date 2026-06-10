from decimal import Decimal
from pages.base_page import BasePage
from utils.price_parser import PriceParser


class CartPage(BasePage):
    """Shopping cart page object for total validation."""

    PRECISE_TOTAL_SELECTORS = [
        "[data-test-id='CART_TOTAL']",
        "[data-test-id='SUBTOTAL']",
        "[data-test-id='ITEM_TOTAL']",
        "[data-test-id*='cart-total' i]",
        "[data-test-id*='subtotal' i]",
        "[data-test-id*='total' i]",
        "[aria-label*='Subtotal' i]",
        "[aria-label*='Total' i]",
    ]

    TEXT_TOTAL_SELECTORS = [
        "xpath=//*[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'subtotal')]",
        "xpath=//*[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'total')]",
    ]

    def assert_cart_total_not_exceeds(self, budget_per_item: int | float, items_count: int) -> None:
        self.open_cart()
        total = self._read_cart_total()
        threshold = Decimal(str(budget_per_item)) * Decimal(str(items_count))
        self.screenshot("cart_total_page")

        assert total <= threshold, (
            f"Cart total {total} exceeds allowed budget {threshold}. "
            f"Budget per item={budget_per_item}, items count={items_count}."
        )

    # CamelCase wrapper matching the exercise wording.
    def assertCartTotalNotExceeds(self, budgetPerItem: int | float, itemsCount: int) -> None:
        self.assert_cart_total_not_exceeds(budgetPerItem, itemsCount)

    def open_cart(self) -> None:
        # eBay cart path may redirect to cart.ebay.com while preserving session cookies.
        self.open("cart")
        self.dismiss_known_popups()

    def _read_cart_total(self) -> Decimal:
        precise_total = self._read_total_from_precise_selectors()
        if precise_total is not None:
            return precise_total

        text_total = self._read_total_from_text_selectors()
        if text_total is not None:
            return text_total

        body_text = self.page.locator("body").inner_text(timeout=5000)
        text_total = self._extract_total_from_cart_text(body_text)
        if text_total is not None:
            return text_total

        # Last fallback: parse the full cart page and use the highest currency value seen.
        # This is intentionally last because eBay may show shipping, recommendations, and discounts.
        fallback_price = PriceParser.highest_price(body_text)
        if fallback_price is not None:
            return fallback_price

        self.screenshot("cart_total_not_found")
        raise AssertionError("Could not read cart subtotal or total from the cart page.")

    def _read_total_from_precise_selectors(self) -> Decimal | None:
        for selector in self.PRECISE_TOTAL_SELECTORS:
            try:
                locator = self.page.locator(selector).first
                if locator.is_visible(timeout=2000):
                    price = PriceParser.highest_price(locator.inner_text(timeout=2000))
                    if price is not None:
                        return price
            except Exception:
                continue
        return None

    def _read_total_from_text_selectors(self) -> Decimal | None:
        for selector in self.TEXT_TOTAL_SELECTORS:
            try:
                locator = self.page.locator(selector).first
                if locator.is_visible(timeout=2000):
                    price = PriceParser.highest_price(locator.inner_text(timeout=2000))
                    if price is not None:
                        return price
            except Exception:
                continue
        return None

    def _extract_total_from_cart_text(self, text: str) -> Decimal | None:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        keywords = ["subtotal", "item total", "cart total", "order total", "total"]

        # First try a single line containing the total keyword and a price.
        for keyword in keywords:
            for line in lines:
                if keyword in line.lower():
                    price = PriceParser.highest_price(line)
                    if price is not None:
                        return price

        # Then try a small window because many cart pages put the label and amount on separate lines.
        for index, line in enumerate(lines):
            if any(keyword in line.lower() for keyword in keywords):
                window = " ".join(lines[index : index + 4])
                price = PriceParser.highest_price(window)
                if price is not None:
                    return price

        return None
