"""
Configuration settings for end-to-end and browser tests.

This module centralizes configuration settings for all browser and end-to-end tests,
ensuring consistency across test files.
"""

import os
import socket

# Server URL for browser tests
SERVER_URL = "http://localhost:8000"

# Test user default password
DEFAULT_TEST_PASSWORD = "testpassword123"

# Browser configuration
BROWSER_CONFIG = {
    "headless": True,  # Set to False to watch tests in browser
    "slow_mo": 100,    # Slow down browser actions (ms)
    "browser_type": "chromium",  # "chromium", "firefox", or "webkit"
    "default_timeout": 5000,
    "navigation_timeout": 10000,
}

# Viewport configurations
VIEWPORTS = {
    "desktop": {"width": 1280, "height": 800},
    "tablet": {"width": 768, "height": 1024},
    "mobile": {"width": 375, "height": 667}
}

# Screenshot directories
SCREENSHOTS_BASE_DIR = "test_screenshots"
SCREENSHOTS_DIRS = {
    "account": f"{SCREENSHOTS_BASE_DIR}/account",
    "todo": f"{SCREENSHOTS_BASE_DIR}/todo",
    "admin": f"{SCREENSHOTS_BASE_DIR}/admin",
    "visual": f"{SCREENSHOTS_BASE_DIR}/visual",
    "ai": f"{SCREENSHOTS_BASE_DIR}/ai_testing",
}

# Test report directory
REPORTS_DIR = "test_reports/browser"

# Ensure all directories exist
def ensure_directories():
    """Create all required directories if they don't exist."""
    os.makedirs(REPORTS_DIR, exist_ok=True)
    for dir_path in SCREENSHOTS_DIRS.values():
        os.makedirs(dir_path, exist_ok=True)

# Check if server is running
def is_server_running(host="localhost", port=8000):
    """Check if the Django server is running."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex((host, port))
    sock.close()
    return result == 0