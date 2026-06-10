# Playwright Python eBay Automation Exercise

This repository implements an end-to-end automation scenario for a live commerce website using **Python + Playwright**.

The scenario covers:

1. Authentication / guest setup
2. Product search by name and maximum price
3. Collection of up to `N` product URLs using XPath and paging
4. Adding selected items to the cart
5. Returning to the search results page after each item is added
6. Validating that the cart total does not exceed `budgetPerItem * itemsCount`
7. Screenshots, Playwright trace, pytest HTML report, and optional Allure output

---

## Tech Stack

* Python 3.11+
* Playwright
* Pytest
* Pytest HTML report
* Optional Allure report support
* Page Object Model
* Object-Oriented Programming
* JSON data-driven test input

---

## Main Functions

The required project functions are implemented as Page Object methods:

| Project requirement                                    | Python implementation                                |
| ------------------------------------------------------ | ---------------------------------------------------- |
| Authentication                                         | `LoginPage.authenticate()`                           |
| `searchItemsByNameUnderPrice(query, maxPrice, limit)`  | `SearchResultsPage.searchItemsByNameUnderPrice(...)` |
| `addItemsToCart(urls)`                                 | `ItemPage.addItemsToCart(...)`                       |
| `assertCartTotalNotExceeds(budgetPerItem, itemsCount)` | `CartPage.assertCartTotalNotExceeds(...)`            |

Pythonic `snake_case` methods are also available internally, while the camelCase wrappers are kept to match the exercise wording.

---

## Project Structure

```text
playwright-python-ebay-automation/
├── config/
│   ├── __init__.py
│   └── settings.py
├── data/
│   └── search_data.json
├── pages/
│   ├── __init__.py
│   ├── base_page.py
│   ├── login_page.py
│   ├── search_results_page.py
│   ├── item_page.py
│   └── cart_page.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   └── test_ebay_cart_budget.py
├── utils/
│   ├── __init__.py
│   ├── file_utils.py
│   ├── json_data_loader.py
│   └── price_parser.py
├── reports/
├── screenshots/
├── traces/
├── .env.example
├── pytest.ini
├── requirements.txt
└── README.md
```

---

## Test Data

The test data is externalized in:

```text
data/search_data.json
```

The JSON file uses two scenario groups:

```json
{
  "e2e_scenarios": [
    {
      "name": "nike_air_max_susan_under_400_aud",
      "query": "Nike Air Max 1 Susan CK6643-100",
      "max_price": 400,
      "limit": 5,
      "currency": "AUD"
    }
  ],
  "search_only_scenarios": [
    {
      "name": "Sony Clie",
      "query": "Sony Clie PEG-TG50",
      "max_price": 400,
      "limit": 5,
      "currency": "AUD"
    }
  ]
}
```

### `e2e_scenarios`

These scenarios run the full end-to-end flow:

```text
Authentication → Search → Add items to cart → Validate cart total
```

The full E2E scenario requires at least one result because it must add items to the cart.

### `search_only_scenarios`

These scenarios test only the search function. They are used to prove that `searchItemsByNameUnderPrice()` can return fewer than the requested limit, including zero results, without failing.

This covers the project requirement:

```text
If fewer results are found, return what exists; returning zero results is valid.
```

---

## Install and Run

### 1. Create a virtual environment

```bash
python -m venv .venv
```

### 2. Activate the virtual environment

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m playwright install chromium
```

### 4. Optional environment configuration

Copy the example environment file:

```bash
cp .env.example .env
```

On Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

If `EBAY_USERNAME` and `EBAY_PASSWORD` are empty, the test runs in guest mode.

Example `.env`:

```env
BASE_URL=https://www.ebay.com.au
HEADLESS=false
SLOW_MO_MS=0
DEFAULT_TIMEOUT_MS=15000
EBAY_USERNAME=
EBAY_PASSWORD=
```

---

## Running Tests

### Run all tests

```bash
pytest
```

### Run all tests with browser visible - Windows PowerShell

```powershell
$env:HEADLESS="false"
pytest -s
```

### Run all tests in headless mode - Windows PowerShell

```powershell
$env:HEADLESS="true"
pytest -s
```

### Run with slower browser actions - Windows PowerShell

```powershell
$env:HEADLESS="false"
$env:SLOW_MO_MS="500"
pytest -s
```

### Run only the full E2E scenario

```powershell
pytest -m e2e -s
```

### Run the exact E2E test

```powershell
pytest "tests/test_ebay_cart_budget.py::test_search_add_to_cart_and_validate_budget[nike_air_max_susan_under_400_aud]" -s
```

### Run the search-only zero/fewer-than-limit test

```powershell
pytest "tests/test_ebay_cart_budget.py::test_search_items_by_name_under_price_allows_zero_or_fewer_than_limit[zero_or_fewer_results_allowed]" -s
```

### Check test discovery only

```powershell
python -m pytest --collect-only
```

Expected result:

```text
collected 2 items
```

---

## Reports and Evidence

After a run, the framework can generate:

```text
reports/report.html
reports/allure_results/
reports/run.log
screenshots/*.png
traces/*.zip
reports/videos/*
```

Open the pytest HTML report:

```text
reports/report.html
```

Open a Playwright trace:

```bash
playwright show-trace traces/<trace-file>.zip
```

Run Allure locally if the Allure CLI is installed:

```bash
allure serve reports/allure_results
```

---

## Architecture Notes

Each website area is represented by a dedicated Page Object:

* `LoginPage` handles authentication or guest mode.
* `SearchResultsPage` handles search, optional price filtering, XPath result extraction, and paging.
* `ItemPage` handles product details, random variant selection, add-to-cart, screenshots, and returning to the saved search results page.
* `CartPage` handles cart total extraction and assertion.
* `BasePage` contains shared functionality such as screenshots, opening URLs, popup dismissal, and anti-bot challenge detection.

---

## Full Scenario Example

```python
LoginPage(page, settings).authenticate()

urls = SearchResultsPage(page, settings).searchItemsByNameUnderPrice(
    query="Nike Air Max 1 Susan CK6643-100",
    maxPrice=400,
    limit=5,
)

ItemPage(page, settings).addItemsToCart(urls)

CartPage(page, settings).assertCartTotalNotExceeds(
    budgetPerItem=400,
    itemsCount=len(urls),
)
```

---

## Assumptions and Limitations

1. eBay is a live website, so UI selectors, anti-bot protection, CAPTCHA, login MFA, stock availability, and shipping/location rules can change.
2. The default flow uses guest mode. Real login is attempted only if credentials are supplied through environment variables.
3. Some items require mandatory variants such as size or color. The framework attempts to select random available dropdown, button, or radio variants.
4. Prices are parsed from visible text. The final budget assertion uses the cart total/subtotal visible on the site.
5. Currency is assumed to be AUD when using `https://www.ebay.com.au`.
6. The framework bypass CAPTCHA, MFA, or anti-bot protection.
7. Live e-commerce tests may be flaky if the website changes or blocks automation traffic.

---

## Summary

This project satisfies the requested automation task by implementing:

* Playwright with Python
* Page Object Model
* Object-Oriented design
* JSON data-driven test input
* Authentication / guest setup
* Product search with price condition
* XPath-based item extraction
* Pagination support
* Add-to-cart flow
* Cart total validation
* Screenshots, trace, pytest HTML report, and optional Allure results
