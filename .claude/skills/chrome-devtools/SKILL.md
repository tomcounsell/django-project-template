---
name: chrome-devtools
description: Browser automation and testing via Chrome DevTools Protocol
triggers:
  - "test the page"
  - "check the browser"
  - "take a screenshot"
  - "browser automation"
  - "console errors"
  - "network requests"
  - "click on"
  - "navigate to"
mcp_source: "@anthropic/mcp-server-chrome"
---

# Chrome DevTools Skill

Browser automation and testing via Chrome DevTools Protocol. This skill manages both the Chrome browser instance AND the MCP server that communicates with it.

## Overview

Unlike most MCP skills that just wrap an existing server, this skill:

1. **Launches Chrome** with remote debugging enabled on port 9222
2. **Starts the MCP server** connected to that Chrome instance
3. **Maintains browser state** across tool calls (same page, same session)
4. **Cleans up both** when the session ends

## Architecture

```
┌─────────────────┐     stdin/stdout      ┌─────────────────┐     CDP        ┌─────────────────┐
│  Claude Code    │ ◄──── JSON-RPC ─────► │  MCP Server     │ ◄───────────► │  Chrome         │
│  (skill script) │                       │  (subprocess)   │     :9222      │  (subprocess)   │
└─────────────────┘                       └─────────────────┘                └─────────────────┘
```

## Available Tools

### Navigation (3 tools)
- **navigate** - Navigate to a URL
- **go_back** - Go back in browser history
- **go_forward** - Go forward in browser history

### Interaction (4 tools)
- **click** - Click an element by CSS selector
- **type** - Type text into a focused element
- **fill** - Fill a form field by selector
- **scroll** - Scroll the page

### Inspection (5 tools)
- **screenshot** - Take a screenshot (full page or viewport)
- **get_console_logs** - Get browser console messages
- **get_network_requests** - Get network request log
- **evaluate** - Execute JavaScript in page context
- **get_page_content** - Get current page HTML

### Page Info (2 tools)
- **get_url** - Get current page URL
- **get_title** - Get current page title

## Usage

### Starting a Browser Session

```python
from chrome_devtools_session import ChromeDevToolsSession

# Using context manager (recommended - ensures cleanup)
with ChromeDevToolsSession() as session:
    # Navigate to a page
    session.call_tool("navigate", {"url": "https://example.com"})

    # Take a screenshot
    screenshot = session.call_tool("screenshot", {"fullPage": True})

    # Check for console errors
    logs = session.call_tool("get_console_logs", {})
    errors = [log for log in logs if log.get("level") == "error"]

    # Click a button
    session.call_tool("click", {"selector": "#submit-button"})
```

### Common Workflows

#### Testing a Login Flow
```python
with ChromeDevToolsSession() as session:
    session.call_tool("navigate", {"url": "https://app.example.com/login"})
    session.call_tool("fill", {"selector": "#email", "value": "test@example.com"})
    session.call_tool("fill", {"selector": "#password", "value": "password123"})
    session.call_tool("click", {"selector": "button[type=submit]"})

    # Wait for navigation and check result
    import time
    time.sleep(2)

    url = session.call_tool("get_url", {})
    assert "/dashboard" in url, "Login failed - not redirected to dashboard"
```

#### Checking for JavaScript Errors
```python
with ChromeDevToolsSession() as session:
    session.call_tool("navigate", {"url": "https://example.com"})

    # Interact with the page to trigger potential errors
    session.call_tool("click", {"selector": ".interactive-element"})

    # Check console for errors
    logs = session.call_tool("get_console_logs", {})
    errors = [log for log in logs if log.get("level") == "error"]

    if errors:
        print("JavaScript errors found:")
        for error in errors:
            print(f"  - {error.get('text')}")
```

#### Monitoring Network Requests
```python
with ChromeDevToolsSession() as session:
    session.call_tool("navigate", {"url": "https://api.example.com"})

    requests = session.call_tool("get_network_requests", {})

    # Find failed requests
    failed = [r for r in requests if r.get("status", 200) >= 400]

    # Find slow requests
    slow = [r for r in requests if r.get("duration", 0) > 1000]
```

## CLI Usage

```bash
# Start interactive session
python chrome_devtools_session.py --interactive

# List available tools
python chrome_devtools_session.py --list-tools

# Single tool call
python chrome_devtools_session.py --tool navigate --args '{"url": "https://example.com"}'
```

## Configuration

### Chrome Path

The skill auto-detects Chrome on macOS and Linux. Set `CHROME_PATH` to override:

```bash
export CHROME_PATH="/path/to/chrome"
```

### Debug Port

Default: 9222. Set `CHROME_DEBUG_PORT` to change:

```bash
export CHROME_DEBUG_PORT=9333
```

### Headless Mode

By default, Chrome runs headless (no visible window). Set `CHROME_HEADLESS=false` to see the browser:

```bash
export CHROME_HEADLESS=false
```

## Troubleshooting

### Chrome Won't Start

1. Check Chrome is installed
2. Verify no other Chrome is using port 9222
3. Try killing existing Chrome processes: `pkill -f "chrome.*remote-debugging"`

### MCP Server Connection Failed

1. Ensure Chrome started successfully (check stderr output)
2. Wait a moment for Chrome to initialize
3. Try increasing the startup delay in the session script

### Screenshots Return Empty

1. Page may not have finished loading - add a delay
2. Check page dimensions with `evaluate` tool
3. Try `fullPage: false` for viewport-only screenshot
