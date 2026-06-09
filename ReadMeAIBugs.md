# ReadMeAIBugs

## Original Code Under Review

```python
from playwright.sync_api import sync_playwright
from selenium import webdriver
import time


def test_search_functionality():
    browser = sync_playwright().start().chromium.launch()
    page = browser.new_page()
    page.goto("https://example.com")

    time.sleep(2)

    search_box = page.locator("#search")
    search_box.fill("playwright testing")

    page.locator(".button").click()

    time.sleep(3)

    results = page.locator(".result-item")

    browser.close()
```

---

## Issue 1: Playwright lifecycle is not managed correctly

### Problem

The code uses:

```python
browser = sync_playwright().start().chromium.launch()
```

This starts Playwright but never stops the Playwright driver. Only the browser is closed. If the test fails before `browser.close()`, the browser can also remain open.

### Fix

Use a context manager so Playwright is always stopped:

```python
with sync_playwright() as playwright:
    browser = playwright.chromium.launch()
    page = browser.new_page()
    # test steps
    browser.close()
```

A stronger pytest-based solution is to put browser creation and cleanup in fixtures.

---

## Issue 2: Selenium is imported but not used

### Problem

The code imports Selenium:

```python
from selenium import webdriver
```

But the test uses Playwright only. Mixing Selenium and Playwright in the same test creates confusion and unnecessary dependencies.

### Fix

Remove the Selenium import:

```python
from playwright.sync_api import sync_playwright
import time
```

Better still, remove `time` as well and use Playwright waiting mechanisms.

---

## Issue 3: `time.sleep()` creates slow and flaky tests

### Problem

The code uses fixed waits:

```python
time.sleep(2)
time.sleep(3)
```

This is unreliable. The page may be ready earlier, which wastes time, or later, which causes failures.

### Fix

Use Playwright auto-waiting and assertions:

```python
search_box = page.locator("#search")
search_box.wait_for(state="visible")
search_box.fill("playwright testing")
```

After clicking Search:

```python
page.locator(".button").click()
page.locator(".result-item").first.wait_for(state="visible")
```

---

## Issue 4: No assertions are performed

### Problem

The test creates a locator:

```python
results = page.locator(".result-item")
```

But it never checks whether results exist. A test without assertions can pass even when the feature is broken.

### Fix

Use Playwright expectations:

```python
from playwright.sync_api import expect

results = page.locator(".result-item")
expect(results.first).to_be_visible()
assert results.count() > 0
```

---

## Issue 5: Selectors are too generic

### Problem

The selector `.button` is very broad:

```python
page.locator(".button").click()
```

Many pages can contain several elements with this class. The test may click the wrong button.

### Fix

Use semantic or specific locators:

```python
page.get_by_role("button", name="Search").click()
```

Or use a stable test id if the application provides one:

```python
page.get_by_test_id("search-button").click()
```

---

## Issue 6: Browser cleanup is not protected if the test fails

### Problem

If any line before `browser.close()` fails, the browser remains open.

### Fix

Use `try/finally` or a context manager:

```python
with sync_playwright() as playwright:
    browser = playwright.chromium.launch()
    try:
        page = browser.new_page()
        page.goto("https://example.com")
        # test steps
    finally:
        browser.close()
```

---

## Corrected Version

```python
from playwright.sync_api import sync_playwright, expect


def test_search_functionality():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        page = browser.new_page()

        try:
            page.goto("https://example.com", wait_until="domcontentloaded")

            search_box = page.locator("#search")
            expect(search_box).to_be_visible()
            search_box.fill("playwright testing")

            page.get_by_role("button", name="Search").click()

            results = page.locator(".result-item")
            expect(results.first).to_be_visible()
            assert results.count() > 0

        finally:
            browser.close()
```

---

## Recommended Final Improvement

For a production framework, move browser setup to pytest fixtures and move page actions into Page Object classes. This improves reusability, readability, and maintainability.
