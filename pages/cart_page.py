from decimal import Decimal
from pages.base_page import BasePage
from utils.price_parser import PriceParser


class CartPage(BasePage):
    """Shopping cart page object for total validation."""

    TOTAL_SELECTORS = [
        "[data-test-id='CART_TOTAL']",
        "[data-test-id='SUBTOTAL']",
        "[data-test-id*='TOTAL']",
        "xpath=//*[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'subtotal')]",
        "xpath=//*[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'total')]",
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
        for selector in self.TOTAL_SELECTORS:
            try:
                locator = self.page.locator(selector).first
                if locator.is_visible(timeout=2500):
                    text = locator.inner_text(timeout=2500)
                    price = PriceParser.highest_price(text)
                    if price is not None:
                        return price
            except Exception:
                continue

        # Fallback: parse the full cart page and use the highest currency value seen.
        body_text = self.page.locator("body").inner_text(timeout=5000)
        price = PriceParser.highest_price(body_text)
        if price is None:
            self.screenshot("cart_total_not_found")
            raise AssertionError("Could not read cart subtotal or total from the cart page.")
        return price
