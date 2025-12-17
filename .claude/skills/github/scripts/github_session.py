#!/usr/bin/env python3
"""
GitHub MCP Skill Session

Interact with GitHub repositories, issues, and pull requests.
"""

import json
import sys
from pathlib import Path
from typing import Any

# Import base session
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "_base" / "scripts"))
from mcp_session import MCPSession


class GitHubSession(MCPSession):
    """Session manager for GitHub MCP skill."""

    MCP_COMMAND = ["npx", "-y", "@modelcontextprotocol/server-github@latest"]
    REQUIRED_ENV = ["GITHUB_PERSONAL_ACCESS_TOKEN"]
    OPTIONAL_ENV = []

    # Convenience methods for common operations

    def search_repositories(self, query: str, per_page: int = 10) -> list[dict]:
        """Search for GitHub repositories."""
        return self.call_tool("search_repositories", {
            "query": query,
            "perPage": per_page,
        })

    def get_file_contents(
        self,
        owner: str,
        repo: str,
        path: str,
        branch: str | None = None,
    ) -> dict:
        """Get contents of a file or directory."""
        args = {"owner": owner, "repo": repo, "path": path}
        if branch:
            args["branch"] = branch
        return self.call_tool("get_file_contents", args)

    def list_commits(
        self,
        owner: str,
        repo: str,
        sha: str | None = None,
        per_page: int = 30,
    ) -> list[dict]:
        """List commits in a repository."""
        args = {"owner": owner, "repo": repo, "perPage": per_page}
        if sha:
            args["sha"] = sha
        return self.call_tool("list_commits", args)

    def list_issues(
        self,
        owner: str,
        repo: str,
        state: str = "open",
        labels: list[str] | None = None,
        per_page: int = 30,
    ) -> list[dict]:
        """List issues in a repository."""
        args = {"owner": owner, "repo": repo, "state": state, "per_page": per_page}
        if labels:
            args["labels"] = labels
        return self.call_tool("list_issues", args)

    def get_issue(self, owner: str, repo: str, issue_number: int) -> dict:
        """Get a specific issue."""
        return self.call_tool("get_issue", {
            "owner": owner,
            "repo": repo,
            "issue_number": issue_number,
        })

    def create_issue(
        self,
        owner: str,
        repo: str,
        title: str,
        body: str = "",
        labels: list[str] | None = None,
        assignees: list[str] | None = None,
    ) -> dict:
        """Create a new issue."""
        args = {"owner": owner, "repo": repo, "title": title}
        if body:
            args["body"] = body
        if labels:
            args["labels"] = labels
        if assignees:
            args["assignees"] = assignees
        return self.call_tool("create_issue", args)

    def add_issue_comment(
        self,
        owner: str,
        repo: str,
        issue_number: int,
        body: str,
    ) -> dict:
        """Add a comment to an issue."""
        return self.call_tool("add_issue_comment", {
            "owner": owner,
            "repo": repo,
            "issue_number": issue_number,
            "body": body,
        })

    def list_pull_requests(
        self,
        owner: str,
        repo: str,
        state: str = "open",
        per_page: int = 30,
    ) -> list[dict]:
        """List pull requests."""
        return self.call_tool("list_pull_requests", {
            "owner": owner,
            "repo": repo,
            "state": state,
            "per_page": per_page,
        })

    def get_pull_request(self, owner: str, repo: str, pull_number: int) -> dict:
        """Get a specific pull request."""
        return self.call_tool("get_pull_request", {
            "owner": owner,
            "repo": repo,
            "pull_number": pull_number,
        })

    def create_pull_request(
        self,
        owner: str,
        repo: str,
        title: str,
        head: str,
        base: str,
        body: str = "",
        draft: bool = False,
    ) -> dict:
        """Create a new pull request."""
        return self.call_tool("create_pull_request", {
            "owner": owner,
            "repo": repo,
            "title": title,
            "head": head,
            "base": base,
            "body": body,
            "draft": draft,
        })

    def create_pull_request_review(
        self,
        owner: str,
        repo: str,
        pull_number: int,
        event: str,
        body: str = "",
    ) -> dict:
        """Submit a pull request review."""
        return self.call_tool("create_pull_request_review", {
            "owner": owner,
            "repo": repo,
            "pull_number": pull_number,
            "event": event,  # APPROVE, REQUEST_CHANGES, COMMENT
            "body": body,
        })

    def merge_pull_request(
        self,
        owner: str,
        repo: str,
        pull_number: int,
        merge_method: str = "merge",
    ) -> dict:
        """Merge a pull request."""
        return self.call_tool("merge_pull_request", {
            "owner": owner,
            "repo": repo,
            "pull_number": pull_number,
            "merge_method": merge_method,  # merge, squash, rebase
        })

    def search_code(self, query: str, per_page: int = 30) -> list[dict]:
        """Search code across GitHub."""
        return self.call_tool("search_code", {"q": query, "per_page": per_page})

    def search_issues(self, query: str, per_page: int = 30) -> list[dict]:
        """Search issues and pull requests."""
        return self.call_tool("search_issues", {"q": query, "per_page": per_page})


def parse_repo(repo_str: str) -> tuple[str, str]:
    """Parse owner/repo string."""
    parts = repo_str.split("/")
    if len(parts) != 2:
        raise ValueError(f"Invalid repo format: {repo_str} (expected owner/repo)")
    return parts[0], parts[1]


def main():
    """CLI interface for GitHub skill."""
    import argparse

    parser = argparse.ArgumentParser(description="GitHub MCP Skill")
    parser.add_argument("--issues", metavar="OWNER/REPO", help="List issues")
    parser.add_argument("--prs", metavar="OWNER/REPO", help="List pull requests")
    parser.add_argument("--pr", nargs=2, metavar=("OWNER/REPO", "NUMBER"), help="Get PR details")
    parser.add_argument("--commits", metavar="OWNER/REPO", help="List commits")
    parser.add_argument("--search-repos", metavar="QUERY", help="Search repositories")
    parser.add_argument("--search-code", metavar="QUERY", help="Search code")
    parser.add_argument("--interactive", action="store_true", help="Interactive mode")

    args = parser.parse_args()

    with GitHubSession() as gh:
        if args.issues:
            owner, repo = parse_repo(args.issues)
            issues = gh.list_issues(owner, repo)
            print(f"Open issues in {args.issues}:")
            for issue in issues:
                labels = ", ".join(l.get("name", "") for l in issue.get("labels", []))
                print(f"  #{issue.get('number')}: {issue.get('title')[:50]}")
                if labels:
                    print(f"         Labels: {labels}")
            return

        if args.prs:
            owner, repo = parse_repo(args.prs)
            prs = gh.list_pull_requests(owner, repo)
            print(f"Open PRs in {args.prs}:")
            for pr in prs:
                print(f"  #{pr.get('number')}: {pr.get('title')[:50]}")
                print(f"         {pr.get('head', {}).get('ref')} → {pr.get('base', {}).get('ref')}")
            return

        if args.pr:
            owner, repo = parse_repo(args.pr[0])
            pr = gh.get_pull_request(owner, repo, int(args.pr[1]))
            print(f"PR #{pr.get('number')}: {pr.get('title')}")
            print(f"  State: {pr.get('state')}")
            print(f"  Author: {pr.get('user', {}).get('login')}")
            print(f"  Branch: {pr.get('head', {}).get('ref')} → {pr.get('base', {}).get('ref')}")
            print(f"  Created: {pr.get('created_at')}")
            if pr.get("body"):
                print(f"\n{pr.get('body')[:500]}")
            return

        if args.commits:
            owner, repo = parse_repo(args.commits)
            commits = gh.list_commits(owner, repo, per_page=10)
            print(f"Recent commits in {args.commits}:")
            for commit in commits:
                sha = commit.get("sha", "")[:7]
                msg = commit.get("commit", {}).get("message", "").split("\n")[0][:50]
                author = commit.get("commit", {}).get("author", {}).get("name", "")
                print(f"  {sha} {msg}")
                print(f"         by {author}")
            return

        if args.search_repos:
            repos = gh.search_repositories(args.search_repos)
            print(f"Repositories matching '{args.search_repos}':")
            for repo in repos.get("items", []) if isinstance(repos, dict) else repos:
                print(f"  {repo.get('full_name')} ★{repo.get('stargazers_count', 0)}")
                if repo.get("description"):
                    print(f"    {repo.get('description')[:60]}")
            return

        if args.search_code:
            results = gh.search_code(args.search_code)
            print(f"Code matching '{args.search_code}':")
            items = results.get("items", []) if isinstance(results, dict) else results
            for item in items[:10]:
                print(f"  {item.get('repository', {}).get('full_name')}/{item.get('path')}")
            return

        if args.interactive:
            print(f"GitHub Interactive Mode ({len(gh.tools)} tools)")
            print("Commands: issues owner/repo, prs owner/repo, search <query>, quit")

            while True:
                try:
                    cmd = input("gh> ").strip()
                except (EOFError, KeyboardInterrupt):
                    break

                if not cmd:
                    continue

                if cmd in ("quit", "exit"):
                    break

                parts = cmd.split(maxsplit=1)
                command = parts[0]
                arg = parts[1] if len(parts) > 1 else ""

                try:
                    if command == "issues" and arg:
                        owner, repo = parse_repo(arg)
                        issues = gh.list_issues(owner, repo)
                        for issue in issues[:10]:
                            print(f"  #{issue.get('number')}: {issue.get('title')[:50]}")

                    elif command == "prs" and arg:
                        owner, repo = parse_repo(arg)
                        prs = gh.list_pull_requests(owner, repo)
                        for pr in prs[:10]:
                            print(f"  #{pr.get('number')}: {pr.get('title')[:50]}")

                    elif command == "search" and arg:
                        repos = gh.search_repositories(arg)
                        items = repos.get("items", []) if isinstance(repos, dict) else repos
                        for repo in items[:5]:
                            print(f"  {repo.get('full_name')}")

                    else:
                        print(f"Unknown: {cmd}")
                except Exception as e:
                    print(f"Error: {e}")

            return

        parser.print_help()


if __name__ == "__main__":
    main()
