import pytest

from pages.login_page import LoginPage
from pages.search_results_page import SearchResultsPage
from pages.item_page import ItemPage
from pages.cart_page import CartPage
from utils.json_data_loader import load_test_data


test_data = load_test_data("data/search_data.json")

# Backward compatibility: if the JSON still uses the old "scenarios" key, run those as E2E.
E2E_SCENARIOS = test_data.get("e2e_scenarios") or test_data.get("scenarios") or []
SEARCH_ONLY_SCENARIOS = test_data.get("search_only_scenarios") or []


def _scenario_id(item):
    """Safe pytest id function.

    Pytest can pass an internal NotSet value when a parameter list is empty,
    so do not assume item is always a dictionary.
    """
    if isinstance(item, dict):
        return item.get("name", "scenario")
    return "no_scenario_configured"


def _skip_if_bot_challenge(page_object) -> None:
    if page_object.is_bot_challenge():
        pytest.skip(
            "eBay served an anti-bot challenge (CAPTCHA/splash). "
            "Cannot proceed in this environment; see README limitations."
        )


@pytest.mark.e2e
@pytest.mark.parametrize("scenario", E2E_SCENARIOS, ids=_scenario_id)
def test_search_add_to_cart_and_validate_budget(page, settings, scenario):
    login_page = LoginPage(page, settings)
    login_page.authenticate()
    _skip_if_bot_challenge(login_page)

    search_page = SearchResultsPage(page, settings)
    urls = search_page.searchItemsByNameUnderPrice(
        query=scenario["query"],
        maxPrice=scenario["max_price"],
        limit=scenario.get("limit", 5),
    )
    _skip_if_bot_challenge(search_page)

    assert len(urls) > 0, (
        f"No items were found for query={scenario['query']} "
        f"under max price={scenario['max_price']}. "
        "The full E2E flow needs at least one item to add to cart."
    )

    assert len(urls) <= scenario.get("limit", 5)
    assert all(isinstance(url, str) and url.startswith("http") for url in urls)

    ItemPage(page, settings).addItemsToCart(urls)

    CartPage(page, settings).assertCartTotalNotExceeds(
        budgetPerItem=scenario["max_price"],
        itemsCount=len(urls),
    )


@pytest.mark.parametrize("scenario", SEARCH_ONLY_SCENARIOS, ids=_scenario_id)
def test_search_items_by_name_under_price_allows_zero_or_fewer_than_limit(page, settings, scenario):
    """Covers the requirement that search may return fewer than limit or zero URLs."""
    login_page = LoginPage(page, settings)
    login_page.authenticate()
    _skip_if_bot_challenge(login_page)

    search_page = SearchResultsPage(page, settings)
    urls = search_page.searchItemsByNameUnderPrice(
        query=scenario["query"],
        maxPrice=scenario["max_price"],
        limit=scenario.get("limit", 5),
    )
    _skip_if_bot_challenge(search_page)

    assert isinstance(urls, list)
    assert len(urls) <= scenario.get("limit", 5)
    assert all(isinstance(url, str) and url.startswith("http") for url in urls)
