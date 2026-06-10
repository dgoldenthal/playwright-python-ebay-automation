import pytest

from pages.login_page import LoginPage
from pages.search_results_page import SearchResultsPage
from pages.item_page import ItemPage
from pages.cart_page import CartPage
from utils.json_data_loader import load_test_data


test_data = load_test_data("data/search_data.json")


@pytest.mark.e2e
@pytest.mark.parametrize("scenario", test_data["scenarios"], ids=lambda item: item["name"])
def test_search_add_to_cart_and_validate_budget(page, settings, scenario):
    login_page = LoginPage(page, settings)
    login_page.authenticate()

    search_page = SearchResultsPage(page, settings)
    urls = search_page.searchItemsByNameUnderPrice(
        query=scenario["query"],
        maxPrice=scenario["max_price"],
        limit=scenario.get("limit", 5),
    )

    if search_page.is_bot_challenge():
        pytest.skip(
            "eBay served an anti-bot challenge (CAPTCHA/splash). "
            "Cannot proceed in this environment; see README limitations."
        )

    assert len(urls) > 0, (
        f"No items were found for query={scenario['query']} "
        f"under max price={scenario['max_price']}"
    )

    ItemPage(page, settings).addItemsToCart(urls)

    CartPage(page, settings).assertCartTotalNotExceeds(
        budgetPerItem=scenario["max_price"],
        itemsCount=len(urls),
    )
