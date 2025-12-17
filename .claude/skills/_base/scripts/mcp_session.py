#!/usr/bin/env python3
"""
Base MCP Session Manager

Provides a reusable foundation for MCP skill sessions with:
- Subprocess management for stdin/stdout JSON-RPC
- Protocol initialization and tool discovery
- Environment variable loading from multiple sources
- Robust error handling and cleanup

Usage:
    from mcp_session import MCPSession

    class MySkillSession(MCPSession):
        MCP_COMMAND = ['npx', '-y', '@example/mcp-server@latest']
        REQUIRED_ENV = ['API_KEY']

    session = MySkillSession()
    session.start()
    result = session.call_tool('my_tool', {'arg': 'value'})
    session.stop()
"""

import json
import os
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Any


class MCPSession:
    """Base class for MCP skill sessions."""

    # Override in subclasses
    MCP_COMMAND: list[str] = []
    REQUIRED_ENV: list[str] = []
    OPTIONAL_ENV: list[str] = []
    PROTOCOL_VERSION = "2024-11-05"
    TIMEOUT_SECONDS = 30

    def __init__(self):
        self.process: subprocess.Popen | None = None
        self.msg_id = 0
        self.responses: dict[int, Any] = {}
        self.reader_thread: threading.Thread | None = None
        self._stop_reader = False
        self.tools: list[dict] = []
        self.server_info: dict = {}

    def _load_env_files(self) -> None:
        """Load environment variables from common locations."""
        env_paths = [
            Path.home() / ".env" / "services" / ".env",
            Path.home() / ".env" / ".env",
            Path.cwd() / ".env.local",
            Path.cwd() / ".env",
        ]

        for env_file in env_paths:
            if env_file.exists():
                self._parse_env_file(env_file)

    def _parse_env_file(self, path: Path) -> None:
        """Parse a .env file and set environment variables."""
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, value = line.partition("=")
                    key = key.strip()
                    value = value.strip().strip("'\"")
                    os.environ.setdefault(key, value)

    def _check_required_env(self) -> None:
        """Verify all required environment variables are set."""
        missing = [var for var in self.REQUIRED_ENV if not os.environ.get(var)]
        if missing:
            raise EnvironmentError(
                f"Missing required environment variables: {', '.join(missing)}\n"
                f"Set them in ~/.env/services/.env or .env.local"
            )

    def _build_subprocess_env(self) -> dict[str, str]:
        """Build environment dict for subprocess."""
        env = os.environ.copy()
        # Ensure PATH includes common locations for npx/uvx
        paths = [
            "/usr/local/bin",
            "/opt/homebrew/bin",
            str(Path.home() / ".local" / "bin"),
            str(Path.home() / ".npm-global" / "bin"),
        ]
        existing_path = env.get("PATH", "")
        env["PATH"] = ":".join(paths) + ":" + existing_path
        return env

    def _reader_loop(self) -> None:
        """Background thread that reads JSON-RPC responses from stdout."""
        while not self._stop_reader and self.process:
            try:
                line = self.process.stdout.readline()
                if not line:
                    break
                line = line.strip()
                if not line:
                    continue
                response = json.loads(line)
                msg_id = response.get("id")
                if msg_id is not None:
                    self.responses[msg_id] = response
            except json.JSONDecodeError:
                continue
            except Exception:
                break

    def _send_request(self, method: str, params: dict | None = None) -> dict:
        """Send a JSON-RPC request and wait for response."""
        if not self.process:
            raise RuntimeError("Session not started")

        self.msg_id += 1
        request = {
            "jsonrpc": "2.0",
            "method": method,
            "id": self.msg_id,
        }
        if params:
            request["params"] = params

        request_line = json.dumps(request) + "\n"
        self.process.stdin.write(request_line)
        self.process.stdin.flush()

        # Wait for response
        start = time.time()
        while time.time() - start < self.TIMEOUT_SECONDS:
            if self.msg_id in self.responses:
                response = self.responses.pop(self.msg_id)
                if "error" in response:
                    error = response["error"]
                    raise RuntimeError(
                        f"MCP error {error.get('code')}: {error.get('message')}"
                    )
                return response.get("result", {})
            time.sleep(0.05)

        raise TimeoutError(f"No response for {method} after {self.TIMEOUT_SECONDS}s")

    def _send_notification(self, method: str, params: dict | None = None) -> None:
        """Send a JSON-RPC notification (no response expected)."""
        if not self.process:
            raise RuntimeError("Session not started")

        notification = {
            "jsonrpc": "2.0",
            "method": method,
        }
        if params:
            notification["params"] = params

        notification_line = json.dumps(notification) + "\n"
        self.process.stdin.write(notification_line)
        self.process.stdin.flush()

    def start(self) -> "MCPSession":
        """Start the MCP server subprocess and initialize the session."""
        if not self.MCP_COMMAND:
            raise ValueError("MCP_COMMAND must be set in subclass")

        # Load environment and check requirements
        self._load_env_files()
        self._check_required_env()

        # Start subprocess
        env = self._build_subprocess_env()
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
        self.reader_thread = threading.Thread(target=self._reader_loop, daemon=True)
        self.reader_thread.start()

        # Give the server a moment to start
        time.sleep(0.5)

        # Check if process is still running
        if self.process.poll() is not None:
            stderr = self.process.stderr.read() if self.process.stderr else ""
            raise RuntimeError(f"MCP server failed to start: {stderr}")

        # Initialize protocol
        self._initialize()
        self._discover_tools()

        return self

    def _initialize(self) -> None:
        """Send the MCP initialize handshake."""
        result = self._send_request(
            "initialize",
            {
                "protocolVersion": self.PROTOCOL_VERSION,
                "capabilities": {},
                "clientInfo": {"name": "mcp-skill-session", "version": "1.0.0"},
            },
        )
        self.server_info = result.get("serverInfo", {})

        # Send initialized notification
        self._send_notification("notifications/initialized")

    def _discover_tools(self) -> None:
        """Discover available tools from the MCP server."""
        result = self._send_request("tools/list")
        self.tools = result.get("tools", [])

    def call_tool(self, name: str, arguments: dict | None = None) -> Any:
        """
        Call an MCP tool by name.

        Args:
            name: The tool name
            arguments: Tool arguments as a dictionary

        Returns:
            The tool result (parsed from JSON-RPC response)
        """
        result = self._send_request(
            "tools/call",
            {
                "name": name,
                "arguments": arguments or {},
            },
        )

        # Extract content from result
        content = result.get("content", [])
        if content and len(content) == 1:
            item = content[0]
            if item.get("type") == "text":
                text = item.get("text", "")
                # Try to parse as JSON
                try:
                    return json.loads(text)
                except json.JSONDecodeError:
                    return text
        return content

    def list_tools(self) -> list[dict]:
        """Return the list of available tools."""
        return self.tools

    def get_tool_names(self) -> list[str]:
        """Return just the tool names."""
        return [t.get("name", "") for t in self.tools]

    def stop(self) -> None:
        """Stop the MCP server subprocess and clean up."""
        self._stop_reader = True

        if self.process:
            try:
                self.process.stdin.close()
            except Exception:
                pass

            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            except Exception:
                pass

            self.process = None

        if self.reader_thread:
            self.reader_thread.join(timeout=2)
            self.reader_thread = None

    def __enter__(self) -> "MCPSession":
        """Context manager entry."""
        return self.start()

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.stop()


def introspect_mcp_server(command: list[str], env_vars: dict | None = None) -> dict:
    """
    Introspect an MCP server to discover its tools.

    Args:
        command: The command to start the MCP server
        env_vars: Additional environment variables to set

    Returns:
        Dictionary with server_info and tools
    """

    class TempSession(MCPSession):
        MCP_COMMAND = command

    if env_vars:
        for key, value in env_vars.items():
            os.environ[key] = value

    session = TempSession()
    try:
        session.start()
        return {
            "server_info": session.server_info,
            "tools": session.tools,
        }
    finally:
        session.stop()


if __name__ == "__main__":
    # Example: introspect an MCP server
    if len(sys.argv) < 2:
        print("Usage: python mcp_session.py <mcp-command> [args...]")
        print("Example: python mcp_session.py npx -y @modelcontextprotocol/server-github")
        sys.exit(1)

    command = sys.argv[1:]
    print(f"Introspecting MCP server: {' '.join(command)}")

    try:
        result = introspect_mcp_server(command)
        print(f"\nServer: {result['server_info'].get('name', 'Unknown')}")
        print(f"Tools found: {len(result['tools'])}\n")

        for tool in result["tools"]:
            print(f"  - {tool.get('name')}: {tool.get('description', 'No description')[:60]}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
