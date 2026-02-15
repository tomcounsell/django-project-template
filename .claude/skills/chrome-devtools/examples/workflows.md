# Chrome DevTools Workflows

Common usage patterns for browser testing and automation.

## Testing Login Flows

```python
from chrome_devtools_session import ChromeDevToolsSession

with ChromeDevToolsSession() as browser:
    # Navigate to login page
    browser.navigate("https://app.example.com/login")

    # Fill credentials
    browser.fill("#email", "test@example.com")
    browser.fill("#password", "testpassword")

    # Submit form
    browser.click("button[type=submit]")

    # Wait for page transition
    import time
    time.sleep(2)

    # Verify redirect
    url = browser.call_tool("get_url", {})
    assert "/dashboard" in url, f"Expected dashboard, got {url}"

    # Check for any JavaScript errors during login
    logs = browser.get_console_logs()
    errors = [l for l in logs if l.get("level") == "error"]
    if errors:
        print("Errors during login:")
        for e in errors:
            print(f"  - {e.get('text')}")
```

## Visual Regression Testing

```python
import base64
from pathlib import Path
from chrome_devtools_session import ChromeDevToolsSession

def capture_page_screenshots(urls: list[str], output_dir: Path):
    """Capture screenshots of multiple pages for visual comparison."""
    output_dir.mkdir(exist_ok=True)

    with ChromeDevToolsSession() as browser:
        for url in urls:
            browser.navigate(url)

            # Wait for page to fully load
            import time
            time.sleep(1)

            # Take full-page screenshot
            screenshot_b64 = browser.screenshot(full_page=True)

            # Save to file
            filename = url.replace("https://", "").replace("/", "_") + ".png"
            filepath = output_dir / filename

            with open(filepath, "wb") as f:
                f.write(base64.b64decode(screenshot_b64))

            print(f"Saved: {filepath}")

# Usage
capture_page_screenshots(
    urls=[
        "https://example.com",
        "https://example.com/about",
        "https://example.com/contact",
    ],
    output_dir=Path("./screenshots")
)
```

## API Response Verification

```python
from chrome_devtools_session import ChromeDevToolsSession

with ChromeDevToolsSession() as browser:
    # Navigate to page that makes API calls
    browser.navigate("https://app.example.com/dashboard")

    # Wait for API calls to complete
    import time
    time.sleep(3)

    # Get all network requests
    requests = browser.get_network_requests()

    # Filter for API calls
    api_calls = [r for r in requests if "/api/" in r.get("url", "")]

    print(f"Found {len(api_calls)} API calls:")
    for call in api_calls:
        status = call.get("status", "?")
        url = call.get("url", "unknown")
        duration = call.get("duration", 0)
        print(f"  [{status}] {url} ({duration}ms)")

    # Check for failed requests
    failed = [r for r in api_calls if r.get("status", 200) >= 400]
    if failed:
        print("\nFailed API calls:")
        for r in failed:
            print(f"  - {r.get('url')}: {r.get('status')}")
```

## Form Validation Testing

```python
from chrome_devtools_session import ChromeDevToolsSession

with ChromeDevToolsSession() as browser:
    browser.navigate("https://app.example.com/signup")

    # Test empty form submission
    browser.click("button[type=submit]")

    # Check for validation errors
    import time
    time.sleep(0.5)

    # Look for error elements
    error_count = browser.evaluate(
        "document.querySelectorAll('.error, .invalid, [aria-invalid=true]').length"
    )
    print(f"Validation errors shown: {error_count}")

    # Fill partial form
    browser.fill("#email", "invalid-email")
    browser.click("button[type=submit]")
    time.sleep(0.5)

    # Check email validation
    email_error = browser.evaluate(
        "document.querySelector('#email + .error, #email:invalid')?.textContent || 'none'"
    )
    print(f"Email validation: {email_error}")
```

## Console Error Monitoring

```python
from chrome_devtools_session import ChromeDevToolsSession

def check_page_for_errors(url: str) -> dict:
    """Load a page and report any console errors."""
    with ChromeDevToolsSession() as browser:
        browser.navigate(url)

        # Give time for any async errors
        import time
        time.sleep(2)

        logs = browser.get_console_logs()

        return {
            "url": url,
            "errors": [l for l in logs if l.get("level") == "error"],
            "warnings": [l for l in logs if l.get("level") == "warning"],
            "total_logs": len(logs),
        }

# Check multiple pages
pages = [
    "https://example.com",
    "https://example.com/products",
    "https://example.com/checkout",
]

for page in pages:
    result = check_page_for_errors(page)
    print(f"\n{result['url']}:")
    print(f"  Errors: {len(result['errors'])}")
    print(f"  Warnings: {len(result['warnings'])}")

    if result['errors']:
        for err in result['errors']:
            print(f"    - {err.get('text', 'Unknown error')[:80]}")
```

## Performance Monitoring

```python
from chrome_devtools_session import ChromeDevToolsSession

with ChromeDevToolsSession() as browser:
    browser.navigate("https://app.example.com")

    # Get performance timing
    timing = browser.evaluate("""
        (() => {
            const t = performance.timing;
            return {
                dns: t.domainLookupEnd - t.domainLookupStart,
                tcp: t.connectEnd - t.connectStart,
                ttfb: t.responseStart - t.requestStart,
                download: t.responseEnd - t.responseStart,
                domReady: t.domContentLoadedEventEnd - t.navigationStart,
                load: t.loadEventEnd - t.navigationStart,
            };
        })()
    """)

    print("Performance Timing:")
    print(f"  DNS lookup: {timing.get('dns', '?')}ms")
    print(f"  TCP connect: {timing.get('tcp', '?')}ms")
    print(f"  Time to first byte: {timing.get('ttfb', '?')}ms")
    print(f"  Download: {timing.get('download', '?')}ms")
    print(f"  DOM ready: {timing.get('domReady', '?')}ms")
    print(f"  Full load: {timing.get('load', '?')}ms")

    # Check for slow network requests
    requests = browser.get_network_requests()
    slow = [r for r in requests if r.get("duration", 0) > 500]

    if slow:
        print(f"\nSlow requests (>500ms):")
        for r in slow:
            print(f"  - {r.get('url', '?')[:60]}: {r.get('duration')}ms")
```

## CLI Examples

```bash
# Start interactive browser session
python chrome_devtools_session.py --interactive

# Start with visible browser (not headless)
python chrome_devtools_session.py --headless false --interactive

# Take a single screenshot
python chrome_devtools_session.py --tool navigate --args '{"url": "https://example.com"}'
python chrome_devtools_session.py --tool screenshot --args '{"fullPage": true}'

# Use different debug port
python chrome_devtools_session.py --port 9333 --interactive
```
