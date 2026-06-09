from decimal import Decimal, InvalidOperation
import re


class PriceParser:
    """Utility class for converting e-commerce price text into Decimal values."""

    # Examples handled: "$12.50", "AU $99", "AU $12.50 to AU $50.00"
    _currency_pattern = re.compile(r"(?:AU\s*)?\$\s*([0-9][0-9,]*(?:\.\d{1,2})?)", re.IGNORECASE)

    @classmethod
    def extract_prices(cls, text: str | None) -> list[Decimal]:
        if not text:
            return []

        normalized_text = text.replace("\xa0", " ")
        if "free" in normalized_text.lower():
            return [Decimal("0")]

        prices: list[Decimal] = []
        for raw_value in cls._currency_pattern.findall(normalized_text):
            try:
                prices.append(Decimal(raw_value.replace(",", "")))
            except InvalidOperation:
                continue
        return prices

    @classmethod
    def lowest_price(cls, text: str | None) -> Decimal | None:
        prices = cls.extract_prices(text)
        return min(prices) if prices else None

    @classmethod
    def highest_price(cls, text: str | None) -> Decimal | None:
        prices = cls.extract_prices(text)
        return max(prices) if prices else None
