---
name: github
description: GitHub repository operations and issue management
triggers:
  - "github issue"
  - "pull request"
  - "create PR"
  - "repo"
  - "repository"
  - "github search"
  - "commits"
  - "branches"
mcp_source: "@modelcontextprotocol/server-github"
---

# GitHub Skill

Interact with GitHub repositories, issues, and pull requests directly from Claude Code.

## Overview

This skill provides access to GitHub's API via the official MCP server for:
- Repository management and exploration
- Issue creation and tracking
- Pull request workflows
- Code search and navigation
- Commit history analysis

## Required Environment Variables

- `GITHUB_PERSONAL_ACCESS_TOKEN` - GitHub personal access token

Create a token at: https://github.com/settings/tokens

Required scopes:
- `repo` (for private repositories)
- `read:org` (for organization access)

Set in `~/.env/services/.env`:
```bash
GITHUB_PERSONAL_ACCESS_TOKEN=ghp_xxxxxxxxxxxx
```

## Available Tools

### Repository Operations (5 tools)
- **search_repositories** - Search for repositories
- **get_file_contents** - Get file or directory contents
- **create_repository** - Create a new repository
- **fork_repository** - Fork a repository
- **create_branch** - Create a new branch

### Issue Management (5 tools)
- **list_issues** - List repository issues
- **get_issue** - Get issue details
- **create_issue** - Create a new issue
- **update_issue** - Update an existing issue
- **add_issue_comment** - Add comment to issue

### Pull Requests (8 tools)
- **list_pull_requests** - List PRs with filters
- **get_pull_request** - Get PR details
- **create_pull_request** - Create a new PR
- **get_pull_request_files** - Get files changed in PR
- **get_pull_request_comments** - Get PR review comments
- **get_pull_request_reviews** - Get PR reviews
- **create_pull_request_review** - Submit a review
- **merge_pull_request** - Merge a PR

### Search (3 tools)
- **search_code** - Search code across GitHub
- **search_issues** - Search issues and PRs
- **search_users** - Search GitHub users

### Other (3 tools)
- **list_commits** - List repository commits
- **push_files** - Push multiple files in one commit
- **create_or_update_file** - Create or update a single file

## Usage

### Repository Operations

```python
from github_session import GitHubSession

with GitHubSession() as gh:
    # Search for repositories
    repos = gh.search_repositories("django template language:python")

    # Get file contents
    content = gh.get_file_contents(
        owner="anthropics",
        repo="claude-code",
        path="README.md"
    )

    # List commits
    commits = gh.list_commits(
        owner="myorg",
        repo="myrepo",
        per_page=10
    )
```

### Issue Management

```python
with GitHubSession() as gh:
    # List open issues
    issues = gh.list_issues(
        owner="myorg",
        repo="myrepo",
        state="open"
    )

    # Create an issue
    issue = gh.create_issue(
        owner="myorg",
        repo="myrepo",
        title="Bug: Login fails on Safari",
        body="## Description\n\nLogin button doesn't respond...",
        labels=["bug", "priority:high"]
    )

    # Add a comment
    gh.add_issue_comment(
        owner="myorg",
        repo="myrepo",
        issue_number=issue["number"],
        body="I can reproduce this on Safari 17.0"
    )
```

### Pull Request Workflows

```python
with GitHubSession() as gh:
    # Create a PR
    pr = gh.create_pull_request(
        owner="myorg",
        repo="myrepo",
        title="feat: Add user authentication",
        head="feature/auth",
        base="main",
        body="## Summary\n\n- Adds login/logout\n- Session management"
    )

    # Get PR details
    pr_info = gh.get_pull_request(
        owner="myorg",
        repo="myrepo",
        pull_number=pr["number"]
    )

    # Review a PR
    gh.create_pull_request_review(
        owner="myorg",
        repo="myrepo",
        pull_number=123,
        event="APPROVE",
        body="LGTM!"
    )

    # Merge PR
    gh.merge_pull_request(
        owner="myorg",
        repo="myrepo",
        pull_number=123,
        merge_method="squash"
    )
```

### Code Search

```python
with GitHubSession() as gh:
    # Search for code
    results = gh.search_code(
        query="filename:settings.py DATABASES repo:myorg/myrepo"
    )

    # Search issues across repos
    issues = gh.search_issues(
        query="is:open is:issue label:bug org:myorg"
    )
```

## CLI Usage

```bash
# List issues
python github_session.py --issues myorg/myrepo

# Get PR details
python github_session.py --pr myorg/myrepo 123

# Search repositories
python github_session.py --search-repos "django rest framework"

# Interactive mode
python github_session.py --interactive
```

## Search Query Syntax

### Repository Search
```
django stars:>1000 language:python
react topic:framework
```

### Code Search
```
filename:settings.py DATABASES
extension:py class HttpRequest
repo:django/django path:django/http
```

### Issue Search
```
is:open is:issue label:bug
is:pr is:merged author:username
repo:owner/repo in:title error
```

## Notes

- Rate limits apply (5000 requests/hour for authenticated users)
- Some operations require specific token scopes
- For large repositories, use pagination parameters
