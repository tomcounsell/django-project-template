# GitHub Workflows

Common patterns for repository management and collaboration.

## Issue Triage

```python
from github_session import GitHubSession

with GitHubSession() as gh:
    # Get all open bugs
    bugs = gh.list_issues(
        owner="myorg",
        repo="myrepo",
        state="open",
        labels=["bug"]
    )

    print(f"Open bugs: {len(bugs)}\n")

    # Categorize by priority
    high = [i for i in bugs if any(l.get("name") == "priority:high" for l in i.get("labels", []))]
    normal = [i for i in bugs if i not in high]

    print("High priority:")
    for issue in high:
        print(f"  #{issue.get('number')}: {issue.get('title')[:50]}")

    print("\nNormal priority:")
    for issue in normal[:5]:
        print(f"  #{issue.get('number')}: {issue.get('title')[:50]}")
```

## PR Review Workflow

```python
with GitHubSession() as gh:
    # Get PRs awaiting review
    prs = gh.list_pull_requests(
        owner="myorg",
        repo="myrepo",
        state="open"
    )

    for pr in prs:
        pr_num = pr.get("number")

        # Get review status
        reviews = gh.call_tool("get_pull_request_reviews", {
            "owner": "myorg",
            "repo": "myrepo",
            "pull_number": pr_num
        })

        # Check for approvals
        approvals = [r for r in reviews if r.get("state") == "APPROVED"]

        print(f"PR #{pr_num}: {pr.get('title')[:40]}")
        print(f"   Approvals: {len(approvals)} | Author: {pr.get('user', {}).get('login')}")

        # Get files changed
        files = gh.call_tool("get_pull_request_files", {
            "owner": "myorg",
            "repo": "myrepo",
            "pull_number": pr_num
        })
        print(f"   Files changed: {len(files)}")
```

## Automated Issue Creation

```python
with GitHubSession() as gh:
    # Create a bug report
    issue = gh.create_issue(
        owner="myorg",
        repo="myrepo",
        title="Bug: Login fails on Safari 17",
        body="""## Description

Login button doesn't respond to clicks on Safari 17.0.

## Steps to Reproduce

1. Open app in Safari 17
2. Click "Login"
3. Nothing happens

## Expected Behavior

Login modal should appear.

## Environment

- Browser: Safari 17.0
- OS: macOS Sonoma
- Device: MacBook Pro M3
""",
        labels=["bug", "browser-compatibility", "priority:high"],
        assignees=["developer-username"]
    )

    print(f"Created issue #{issue.get('number')}")
```

## Release Notes Generation

```python
with GitHubSession() as gh:
    # Get merged PRs since last release
    prs = gh.search_issues(
        query="repo:myorg/myrepo is:pr is:merged merged:>2024-01-01"
    )

    # Categorize by label
    features = []
    bugfixes = []
    other = []

    for pr in prs.get("items", []):
        labels = [l.get("name") for l in pr.get("labels", [])]
        if "feature" in labels or "enhancement" in labels:
            features.append(pr)
        elif "bug" in labels or "fix" in labels:
            bugfixes.append(pr)
        else:
            other.append(pr)

    print("# Release Notes\n")
    print("## Features")
    for pr in features:
        print(f"- {pr.get('title')} (#{pr.get('number')})")

    print("\n## Bug Fixes")
    for pr in bugfixes:
        print(f"- {pr.get('title')} (#{pr.get('number')})")
```

## Repository Analysis

```python
with GitHubSession() as gh:
    # Get recent activity
    commits = gh.list_commits(
        owner="myorg",
        repo="myrepo",
        per_page=50
    )

    # Count commits by author
    by_author = {}
    for commit in commits:
        author = commit.get("commit", {}).get("author", {}).get("name", "Unknown")
        by_author[author] = by_author.get(author, 0) + 1

    print("Commits by author (last 50):")
    for author, count in sorted(by_author.items(), key=lambda x: x[1], reverse=True):
        print(f"  {author}: {count}")

    # Check open issues vs PRs
    issues = gh.list_issues(owner="myorg", repo="myrepo", state="open")
    prs = gh.list_pull_requests(owner="myorg", repo="myrepo", state="open")

    print(f"\nOpen issues: {len(issues)}")
    print(f"Open PRs: {len(prs)}")
```

## Code Search

```python
with GitHubSession() as gh:
    # Find all TODO comments
    todos = gh.search_code(
        query="TODO repo:myorg/myrepo"
    )

    print("TODOs in codebase:")
    for item in todos.get("items", [])[:10]:
        print(f"  {item.get('path')}")

    # Find usage of deprecated function
    usages = gh.search_code(
        query="old_function repo:myorg/myrepo extension:py"
    )

    print(f"\nFiles using deprecated function: {len(usages.get('items', []))}")
```

## CLI Examples

```bash
# List open issues
python github_session.py --issues myorg/myrepo

# List open PRs
python github_session.py --prs myorg/myrepo

# Get specific PR
python github_session.py --pr myorg/myrepo 123

# Search repositories
python github_session.py --search-repos "django template"

# Search code
python github_session.py --search-code "filename:settings.py SECRET_KEY"

# Interactive mode
python github_session.py --interactive
```
