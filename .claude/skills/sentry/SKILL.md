---
name: sentry
description: Sentry error tracking and investigation
triggers:
  - "sentry error"
  - "production error"
  - "check errors"
  - "error tracking"
  - "investigate bug"
  - "stack trace"
  - "exception"
  - "crash"
mcp_source: "https://mcp.sentry.dev"
---

# Sentry Skill

Investigate production errors directly from Claude Code using Sentry's MCP server.

## Overview

This skill connects to Sentry's hosted MCP server to:
- Search and filter issues
- Analyze stack traces
- Investigate error patterns
- Get AI-powered root cause analysis

## Required Environment Variables

- `SENTRY_AUTH_TOKEN` - Sentry authentication token with project access

Get your token at: https://sentry.io/settings/account/api/auth-tokens/

Set in `~/.env/services/.env`:
```bash
SENTRY_AUTH_TOKEN=sntryu_xxxxxxxxxxxxx
```

## Available Tools

### Issue Discovery (4 tools)
- **search_issues** - Search for issues with query filters
- **get_issue** - Get detailed issue information
- **list_projects** - List accessible Sentry projects
- **list_organizations** - List accessible organizations

### Analysis (3 tools)
- **get_issue_events** - Get events for an issue
- **get_stacktrace** - Get detailed stack trace for an event
- **get_breadcrumbs** - Get breadcrumb trail for an event

### AI Analysis (2 tools)
- **trigger_seer_analysis** - Start AI root cause analysis
- **get_seer_recommendations** - Get AI-generated fix suggestions

## Usage

### Searching for Issues

```python
from sentry_session import SentrySession

with SentrySession() as sentry:
    # Search for recent errors
    issues = sentry.search_issues(
        query="is:unresolved",
        project="my-project"
    )

    # Search by error type
    type_errors = sentry.search_issues(
        query="TypeError is:unresolved",
        project="my-project"
    )

    # Search in specific file
    file_errors = sentry.search_issues(
        query="stack.filename:*checkout*",
        project="my-project"
    )
```

### Investigating an Issue

```python
with SentrySession() as sentry:
    # Get issue details
    issue = sentry.get_issue("12345")

    print(f"Title: {issue.get('title')}")
    print(f"Occurrences: {issue.get('count')}")
    print(f"Users affected: {issue.get('userCount')}")

    # Get recent events
    events = sentry.get_events("12345", limit=5)

    # Get stack trace for first event
    if events:
        trace = sentry.get_stacktrace(events[0]["id"])
        for frame in trace.get("frames", []):
            print(f"  {frame.get('filename')}:{frame.get('lineno')}")
            print(f"    {frame.get('function')}")
```

### AI-Powered Analysis

```python
with SentrySession() as sentry:
    # Trigger AI analysis
    sentry.trigger_seer_analysis("12345")

    # Get AI recommendations
    recs = sentry.get_seer_recommendations("12345")

    print("AI Analysis:")
    print(f"  Root cause: {recs.get('root_cause')}")
    print(f"  Suggested fix: {recs.get('suggested_fix')}")
```

## Query Syntax

Sentry uses a powerful query language:

| Query | Description |
|-------|-------------|
| `is:unresolved` | Unresolved issues |
| `is:resolved` | Resolved issues |
| `is:ignored` | Ignored issues |
| `level:error` | Error level only |
| `level:fatal` | Fatal errors only |
| `firstSeen:>-7d` | First seen in last 7 days |
| `lastSeen:>-24h` | Active in last 24 hours |
| `user.email:*@example.com` | Errors from specific user |
| `stack.filename:*views.py*` | Errors in views.py |
| `release:1.0.0` | Specific release |
| `environment:production` | Production only |

Combine with AND/OR:
```
is:unresolved level:error environment:production
```

## CLI Usage

```bash
# List projects
python sentry_session.py --projects

# Search for issues
python sentry_session.py --search "is:unresolved level:error" --project my-project

# Get issue details
python sentry_session.py --issue 12345

# Interactive mode
python sentry_session.py --interactive
```

## Common Workflows

### Morning Error Review
```python
with SentrySession() as sentry:
    # Errors since last night
    issues = sentry.search_issues(
        query="is:unresolved lastSeen:>-12h",
        project="my-project"
    )

    for issue in issues:
        print(f"[{issue.get('count')}x] {issue.get('title')}")
```

### Post-Deployment Check
```python
with SentrySession() as sentry:
    # New errors since release
    issues = sentry.search_issues(
        query="is:unresolved firstSeen:>-1h release:latest",
        project="my-project"
    )

    if issues:
        print(f"WARNING: {len(issues)} new issues since deployment")
```

## HTTP vs Subprocess

Unlike most MCP skills, Sentry uses a **hosted HTTP MCP server** at `https://mcp.sentry.dev`. The session manager handles:

1. OAuth-style authentication with `SENTRY_AUTH_TOKEN`
2. HTTP POST requests with JSON-RPC bodies
3. Session management via `Mcp-Session-Id` header
