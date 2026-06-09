# Playwright Python eBay Automation Exercise

This repository implements an end-to-end automation scenario for an e-commerce website using **Python + Playwright**.

The scenario covers:

1. Authentication / guest setup
2. Product search by name and maximum price
3. Collection of up to `N` product URLs using XPath and paging
4. Adding selected items to the cart
5. Validating that the cart total does not exceed `budgetPerItem * itemsCount`
6. Screenshots, Playwright trace, and HTML report generation

---

## Tech Stack

- Python 3.11+
- Playwright
- Pytest
- Pytest HTML report
- Optional Allure report support
- Page Object Model
- OOP
- JSON data-driven test input

---

## Project Structure

```text
playwright_python_ebay_automation/
├── config/
│   └── settings.py
├── data/
│   └── search_data.json
├── pages/
│   ├── base_page.py
│   ├── cart_page.py
│   ├── item_page.py
│   ├── login_page.py
│   └── search_results_page.py
├── tests/
│   ├── conftest.py
│   └── test_ebay_cart_budget.py
├── utils/
│   ├── file_utils.py
│   ├── json_data_loader.py
│   └── price_parser.py
├── ReadMeAIBugs.md
├── pytest.ini
├── requirements.txt
└── README.md
```

---

## Main Functions

The required functions are implemented as Page Object methods:

| Exercise function | Python implementation |
|---|---|
| `searchItemsByNameUnderPrice(query, maxPrice, limit)` | `SearchResultsPage.searchItemsByNameUnderPrice(...)` |
| `addItemsToCart(urls)` | `ItemPage.addItemsToCart(...)` |
| `assertCartTotalNotExceeds(budgetPerItem, itemsCount)` | `CartPage.assertCartTotalNotExceeds(...)` |

Pythonic snake_case methods are also available internally.

---

## Install and Run

### 1. Create a virtual environment

```bash
python -m venv .venv
```

### 2. Activate the environment

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
pip install -r requirements.txt
playwright install chromium
```

### 4. Optional environment configuration

Copy the example environment file:

```bash
cp .env.example .env
```

Example values:

```env
BASE_URL=https://www.ebay.com.au
HEADLESS=false
SLOW_MO_MS=0
DEFAULT_TIMEOUT_MS=15000
EBAY_USERNAME=
EBAY_PASSWORD=
```

If `EBAY_USERNAME` and `EBAY_PASSWORD` are empty, the test runs in **guest mode**.

### 5. Run the test

```bash
pytest
```

Run headed:

```bash
HEADLESS=false pytest
```

Run headless:

```bash
HEADLESS=true pytest
```

---

## Test Data

The test data is externalized in `data/search_data.json`:

```json
{
  "scenarios": [
    {
      "name": "shoes_under_220_aud",
      "query": "shoes",
      "max_price": 220,
      "limit": 5,
      "currency": "AUD"
    }
  ]
}
```

To add more tests, add more objects to the `scenarios` array.

---

## Reports and Evidence

After a run, the following artifacts are created:

```text
reports/report.html
screenshots/*.png
traces/*.zip
reports/videos/*
```

To open a Playwright trace:

```bash
playwright show-trace traces/<trace-file>.zip
```

---

## Architecture Notes

### Page Object Model

Each website area is represented by a dedicated page object:

- `LoginPage` handles authentication or guest mode.
- `SearchResultsPage` handles search, price filtering, XPath result extraction, and paging.
- `ItemPage` handles product details, random variant selection, and add-to-cart.
- `CartPage` handles cart total extraction and assertion.
- `BasePage` contains shared functionality such as screenshots, opening URLs, and popup dismissal.

### Utilities

- `PriceParser` handles dynamic price text such as `AU $12.50`, `$99`, and price ranges.
- `json_data_loader` loads data-driven JSON input.
- `file_utils` handles directories, timestamps, and safe filenames.

---

## Assumptions and Limitations

1. eBay is a live website, so UI selectors, anti-bot protection, CAPTCHA, login MFA, stock availability, and shipping/location rules can change.
2. The default flow uses guest mode. Real login is attempted only if credentials are supplied through environment variables.
3. Some items require mandatory variants such as size or color. The framework attempts to select random available variants.
4. Prices are parsed from visible text. The final budget assertion uses the cart total/subtotal visible on the site.
5. Currency is assumed to be AUD when using `https://www.ebay.com.au`.
6. Live e-commerce tests may be flaky if the website changes or blocks automation traffic.

---

## Example Full Scenario

```python
urls = SearchResultsPage(page, settings).searchItemsByNameUnderPrice("shoes", 220, 5)
ItemPage(page, settings).addItemsToCart(urls)
CartPage(page, settings).assertCartTotalNotExceeds(220, len(urls))
```
