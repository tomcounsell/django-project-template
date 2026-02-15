#!/usr/bin/env python3
"""
Sentry MCP Skill Session

HTTP-based session for Sentry's hosted MCP server.
"""

import json
import os
import sys
from pathlib import Path
from typing import Any

# Try to import requests, fall back to urllib
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    import urllib.request
    import urllib.error
    HAS_REQUESTS = False


class SentrySession:
    """Session manager for Sentry MCP skill (HTTP-based)."""

    MCP_URL = "https://mcp.sentry.dev/sse"
    REQUIRED_ENV = ["SENTRY_AUTH_TOKEN"]
    PROTOCOL_VERSION = "2024-11-05"

    def __init__(self):
        self.msg_id = 0
        self.session_id: str | None = None
        self.token: str | None = None
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
                with open(env_file) as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            key, _, value = line.partition("=")
                            key = key.strip()
                            value = value.strip().strip("'\"")
                            os.environ.setdefault(key, value)

    def _check_required_env(self) -> None:
        """Verify required environment variables."""
        missing = [var for var in self.REQUIRED_ENV if not os.environ.get(var)]
        if missing:
            raise EnvironmentError(
                f"Missing required environment variables: {', '.join(missing)}\n"
                f"Get your Sentry token at: https://sentry.io/settings/account/api/auth-tokens/"
            )

    def _make_request(self, method: str, params: dict | None = None) -> dict:
        """Make an HTTP JSON-RPC request to the Sentry MCP server."""
        self.msg_id += 1

        body = {
            "jsonrpc": "2.0",
            "method": method,
            "id": self.msg_id,
        }
        if params:
            body["params"] = params

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if self.session_id:
            headers["Mcp-Session-Id"] = self.session_id

        if HAS_REQUESTS:
            response = requests.post(
                self.MCP_URL,
                headers=headers,
                json=body,
                timeout=30,
            )
            response.raise_for_status()
            result = response.json()

            # Capture session ID from response headers
            if "Mcp-Session-Id" in response.headers:
                self.session_id = response.headers["Mcp-Session-Id"]
        else:
            req = urllib.request.Request(
                self.MCP_URL,
                data=json.dumps(body).encode(),
                headers=headers,
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode())
                if "Mcp-Session-Id" in response.headers:
                    self.session_id = response.headers["Mcp-Session-Id"]

        if "error" in result:
            error = result["error"]
            raise RuntimeError(f"Sentry MCP error: {error.get('message')}")

        return result.get("result", {})

    def start(self) -> "SentrySession":
        """Initialize the Sentry MCP session."""
        self._load_env_files()
        self._check_required_env()

        self.token = os.environ.get("SENTRY_AUTH_TOKEN")

        # Initialize protocol
        result = self._make_request(
            "initialize",
            {
                "protocolVersion": self.PROTOCOL_VERSION,
                "capabilities": {},
                "clientInfo": {"name": "sentry-skill-session", "version": "1.0.0"},
            },
        )
        self.server_info = result.get("serverInfo", {})

        # Discover tools
        result = self._make_request("tools/list")
        self.tools = result.get("tools", [])

        return self

    def stop(self) -> None:
        """Clean up session (HTTP sessions don't need explicit cleanup)."""
        self.session_id = None

    def __enter__(self) -> "SentrySession":
        return self.start()

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.stop()

    def call_tool(self, name: str, arguments: dict | None = None) -> Any:
        """Call a Sentry MCP tool."""
        result = self._make_request(
            "tools/call",
            {
                "name": name,
                "arguments": arguments or {},
            },
        )

        content = result.get("content", [])
        if content and len(content) == 1:
            item = content[0]
            if item.get("type") == "text":
                text = item.get("text", "")
                try:
                    return json.loads(text)
                except json.JSONDecodeError:
                    return text
        return content

    def list_tools(self) -> list[dict]:
        """Return available tools."""
        return self.tools

    # Convenience methods

    def search_issues(
        self,
        query: str,
        project: str | None = None,
        limit: int = 25,
    ) -> list[dict]:
        """Search for Sentry issues."""
        args = {"query": query, "limit": limit}
        if project:
            args["project"] = project
        return self.call_tool("search_issues", args)

    def get_issue(self, issue_id: str) -> dict:
        """Get details for a specific issue."""
        return self.call_tool("get_issue", {"issue_id": issue_id})

    def get_events(self, issue_id: str, limit: int = 10) -> list[dict]:
        """Get events for an issue."""
        return self.call_tool("get_issue_events", {"issue_id": issue_id, "limit": limit})

    def get_stacktrace(self, event_id: str) -> dict:
        """Get stack trace for an event."""
        return self.call_tool("get_stacktrace", {"event_id": event_id})

    def list_projects(self) -> list[dict]:
        """List accessible Sentry projects."""
        return self.call_tool("list_projects", {})

    def trigger_seer_analysis(self, issue_id: str) -> dict:
        """Trigger AI root cause analysis."""
        return self.call_tool("trigger_seer_analysis", {"issue_id": issue_id})

    def get_seer_recommendations(self, issue_id: str) -> dict:
        """Get AI fix recommendations."""
        return self.call_tool("get_seer_recommendations", {"issue_id": issue_id})


def main():
    """CLI interface for Sentry skill."""
    import argparse

    parser = argparse.ArgumentParser(description="Sentry MCP Skill")
    parser.add_argument("--projects", action="store_true", help="List projects")
    parser.add_argument("--search", help="Search query")
    parser.add_argument("--project", help="Project slug for search")
    parser.add_argument("--issue", help="Get issue details")
    parser.add_argument("--interactive", action="store_true", help="Interactive mode")

    args = parser.parse_args()

    with SentrySession() as sentry:
        if args.projects:
            projects = sentry.list_projects()
            print("Projects:")
            for p in projects:
                print(f"  {p.get('slug')}: {p.get('name')}")
            return

        if args.search:
            issues = sentry.search_issues(args.search, project=args.project)
            print(f"Found {len(issues)} issues:")
            for issue in issues:
                print(f"  [{issue.get('id')}] {issue.get('title')[:60]}")
                print(f"       Count: {issue.get('count')} | Users: {issue.get('userCount')}")
            return

        if args.issue:
            issue = sentry.get_issue(args.issue)
            print(f"Issue {args.issue}:")
            print(f"  Title: {issue.get('title')}")
            print(f"  Level: {issue.get('level')}")
            print(f"  Count: {issue.get('count')}")
            print(f"  Users: {issue.get('userCount')}")
            print(f"  First seen: {issue.get('firstSeen')}")
            print(f"  Last seen: {issue.get('lastSeen')}")
            return

        if args.interactive:
            print(f"Sentry Interactive Mode ({len(sentry.tools)} tools)")
            print("Commands: projects, search <query>, issue <id>, quit")

            while True:
                try:
                    cmd = input("sentry> ").strip()
                except (EOFError, KeyboardInterrupt):
                    break

                if not cmd:
                    continue

                if cmd in ("quit", "exit"):
                    break

                if cmd == "projects":
                    projects = sentry.list_projects()
                    for p in projects:
                        print(f"  {p.get('slug')}")

                elif cmd.startswith("search "):
                    query = cmd[7:]
                    issues = sentry.search_issues(query)
                    for issue in issues[:10]:
                        print(f"  [{issue.get('id')}] {issue.get('title')[:50]}")

                elif cmd.startswith("issue "):
                    issue_id = cmd[6:]
                    issue = sentry.get_issue(issue_id)
                    print(json.dumps(issue, indent=2))

                else:
                    print(f"Unknown: {cmd}")

            return

        parser.print_help()


if __name__ == "__main__":
    main()
