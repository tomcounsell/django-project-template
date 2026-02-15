#!/usr/bin/env python3
"""
Chrome DevTools MCP Skill Session

Manages both Chrome browser and MCP server lifecycle for browser automation.

This skill is special because it:
1. Launches Chrome with remote debugging enabled
2. Starts the MCP server connected to Chrome
3. Maintains state across tool calls
4. Cleans up both processes on exit
"""

import json
import os
import platform
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path

# Import base session
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "_base" / "scripts"))
from mcp_session import MCPSession


def find_chrome() -> str:
    """Find Chrome executable path."""
    # Check environment variable first
    if chrome_path := os.environ.get("CHROME_PATH"):
        if Path(chrome_path).exists():
            return chrome_path

    system = platform.system()

    if system == "Darwin":  # macOS
        paths = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Chromium.app/Contents/MacOS/Chromium",
            "/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary",
        ]
    elif system == "Linux":
        paths = [
            "/usr/bin/google-chrome",
            "/usr/bin/google-chrome-stable",
            "/usr/bin/chromium",
            "/usr/bin/chromium-browser",
            "/snap/bin/chromium",
        ]
    elif system == "Windows":
        paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        ]
    else:
        paths = []

    # Also check PATH
    for cmd in ["google-chrome", "google-chrome-stable", "chromium", "chromium-browser"]:
        if path := shutil.which(cmd):
            paths.insert(0, path)

    for path in paths:
        if Path(path).exists():
            return path

    raise FileNotFoundError(
        "Chrome not found. Install Chrome or set CHROME_PATH environment variable."
    )


class ChromeDevToolsSession(MCPSession):
    """
    Session manager for Chrome DevTools MCP skill.

    Handles lifecycle of both Chrome browser and MCP server.
    """

    MCP_COMMAND = ["npx", "-y", "@anthropic/mcp-server-chrome@latest"]
    REQUIRED_ENV = []
    OPTIONAL_ENV = ["CHROME_PATH", "CHROME_DEBUG_PORT", "CHROME_HEADLESS"]

    def __init__(self):
        super().__init__()
        self.chrome_process: subprocess.Popen | None = None
        self.debug_port = int(os.environ.get("CHROME_DEBUG_PORT", "9222"))
        self.headless = os.environ.get("CHROME_HEADLESS", "true").lower() != "false"

    def _start_chrome(self) -> None:
        """Start Chrome with remote debugging enabled."""
        chrome_path = find_chrome()

        # Build Chrome arguments
        chrome_args = [
            chrome_path,
            f"--remote-debugging-port={self.debug_port}",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-default-apps",
            "--disable-popup-blocking",
            "--disable-translate",
            "--disable-background-timer-throttling",
            "--disable-renderer-backgrounding",
            "--disable-device-discovery-notifications",
            # Use a separate user data dir to avoid conflicts
            f"--user-data-dir={Path.home() / '.chrome-mcp-skill'}",
        ]

        if self.headless:
            chrome_args.append("--headless=new")

        # Start Chrome
        self.chrome_process = subprocess.Popen(
            chrome_args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True,
        )

        # Wait for Chrome to start and open debug port
        time.sleep(2)

        # Verify Chrome is running
        if self.chrome_process.poll() is not None:
            stderr = self.chrome_process.stderr.read().decode() if self.chrome_process.stderr else ""
            raise RuntimeError(f"Chrome failed to start: {stderr}")

        print(f"Chrome started on debug port {self.debug_port}", file=sys.stderr)

    def _stop_chrome(self) -> None:
        """Stop the Chrome browser process."""
        if self.chrome_process:
            try:
                # Send SIGTERM to the process group
                os.killpg(os.getpgid(self.chrome_process.pid), signal.SIGTERM)
                self.chrome_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(os.getpgid(self.chrome_process.pid), signal.SIGKILL)
            except (ProcessLookupError, OSError):
                pass
            finally:
                self.chrome_process = None

    def start(self) -> "ChromeDevToolsSession":
        """Start Chrome and the MCP server."""
        # Load environment
        self._load_env_files()

        # Start Chrome first
        self._start_chrome()

        # Update MCP command to connect to our Chrome instance
        # The MCP server needs to know the debug URL
        self.MCP_COMMAND = [
            "npx", "-y", "@anthropic/mcp-server-chrome@latest",
        ]

        # Set the debug URL for the MCP server
        os.environ["CHROME_DEBUG_URL"] = f"http://localhost:{self.debug_port}"

        # Now start the MCP server
        env = self._build_subprocess_env()
        env["CHROME_DEBUG_URL"] = f"http://localhost:{self.debug_port}"

        self.process = subprocess.Popen(
            self.MCP_COMMAND,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env,
            bufsize=1,
        )

        # Start reader thread
        self._stop_reader = False
        import threading
        self.reader_thread = threading.Thread(target=self._reader_loop, daemon=True)
        self.reader_thread.start()

        # Give the server a moment
        time.sleep(1)

        # Check if process is still running
        if self.process.poll() is not None:
            stderr = self.process.stderr.read() if self.process.stderr else ""
            self._stop_chrome()
            raise RuntimeError(f"MCP server failed to start: {stderr}")

        # Initialize protocol
        self._initialize()
        self._discover_tools()

        print(f"Chrome DevTools session started with {len(self.tools)} tools", file=sys.stderr)
        return self

    def stop(self) -> None:
        """Stop both MCP server and Chrome."""
        # Stop MCP server first
        super().stop()

        # Then stop Chrome
        self._stop_chrome()

        print("Chrome DevTools session stopped", file=sys.stderr)

    def navigate(self, url: str) -> dict:
        """Convenience method: Navigate to a URL."""
        return self.call_tool("navigate", {"url": url})

    def screenshot(self, full_page: bool = True) -> str:
        """Convenience method: Take a screenshot, returns base64 image."""
        result = self.call_tool("screenshot", {"fullPage": full_page})
        return result.get("data", "") if isinstance(result, dict) else result

    def click(self, selector: str) -> dict:
        """Convenience method: Click an element."""
        return self.call_tool("click", {"selector": selector})

    def fill(self, selector: str, value: str) -> dict:
        """Convenience method: Fill a form field."""
        return self.call_tool("fill", {"selector": selector, "value": value})

    def get_console_logs(self) -> list:
        """Convenience method: Get console logs."""
        result = self.call_tool("get_console_logs", {})
        return result if isinstance(result, list) else []

    def get_network_requests(self) -> list:
        """Convenience method: Get network requests."""
        result = self.call_tool("get_network_requests", {})
        return result if isinstance(result, list) else []

    def evaluate(self, expression: str) -> any:
        """Convenience method: Evaluate JavaScript."""
        return self.call_tool("evaluate", {"expression": expression})


def main():
    """CLI interface for Chrome DevTools skill."""
    import argparse

    parser = argparse.ArgumentParser(description="Chrome DevTools MCP Skill")
    parser.add_argument("--list-tools", action="store_true", help="List available tools")
    parser.add_argument("--tool", help="Tool name to call")
    parser.add_argument("--args", help="Tool arguments as JSON string")
    parser.add_argument("--interactive", action="store_true", help="Interactive mode")
    parser.add_argument("--headless", default="true", help="Run Chrome headless (default: true)")
    parser.add_argument("--port", type=int, default=9222, help="Chrome debug port (default: 9222)")

    args = parser.parse_args()

    # Set environment from args
    os.environ["CHROME_HEADLESS"] = args.headless
    os.environ["CHROME_DEBUG_PORT"] = str(args.port)

    with ChromeDevToolsSession() as session:
        if args.list_tools:
            print("Available tools:")
            for tool in session.list_tools():
                print(f"  - {tool['name']}: {tool.get('description', '')[:60]}")
            return

        if args.tool:
            tool_args = {}
            if args.args:
                tool_args = json.loads(args.args)
            result = session.call_tool(args.tool, tool_args)
            print(json.dumps(result, indent=2))
            return

        if args.interactive:
            print(f"{len(session.tools)} tools available. Type 'help' for commands.")
            while True:
                try:
                    cmd = input("> ").strip()
                except (EOFError, KeyboardInterrupt):
                    break

                if not cmd:
                    continue
                if cmd == "help":
                    print("Commands:")
                    print("  list              - List available tools")
                    print("  call <tool> [json] - Call a tool with optional JSON args")
                    print("  nav <url>         - Navigate to URL (shortcut)")
                    print("  shot              - Take screenshot (shortcut)")
                    print("  console           - Get console logs (shortcut)")
                    print("  quit              - Exit")
                elif cmd == "list":
                    for tool in session.list_tools():
                        print(f"  {tool['name']}")
                elif cmd.startswith("call "):
                    parts = cmd[5:].split(" ", 1)
                    tool_name = parts[0]
                    tool_args = {}
                    if len(parts) > 1:
                        tool_args = json.loads(parts[1])
                    result = session.call_tool(tool_name, tool_args)
                    print(json.dumps(result, indent=2))
                elif cmd.startswith("nav "):
                    url = cmd[4:].strip()
                    result = session.navigate(url)
                    print(f"Navigated to {url}")
                elif cmd == "shot":
                    result = session.screenshot()
                    print(f"Screenshot taken ({len(result)} bytes base64)")
                elif cmd == "console":
                    logs = session.get_console_logs()
                    for log in logs:
                        print(f"  [{log.get('level', '?')}] {log.get('text', '')}")
                elif cmd in ("quit", "exit"):
                    break
                else:
                    print(f"Unknown command: {cmd}")
            return

        parser.print_help()


if __name__ == "__main__":
    main()
