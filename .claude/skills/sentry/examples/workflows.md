# Sentry Workflows

Common patterns for error investigation and monitoring.

## Morning Error Triage

```python
from sentry_session import SentrySession

with SentrySession() as sentry:
    # Get all unresolved errors from the last 12 hours
    issues = sentry.search_issues(
        query="is:unresolved lastSeen:>-12h level:error",
        project="my-project"
    )

    print(f"Found {len(issues)} issues to review:\n")

    for issue in sorted(issues, key=lambda x: x.get("count", 0), reverse=True):
        print(f"[{issue.get('count'):>4}x] {issue.get('title')[:60]}")
        print(f"        Users: {issue.get('userCount')} | ID: {issue.get('id')}")
        print()
```

## Post-Deployment Monitoring

```python
with SentrySession() as sentry:
    # Check for new errors since deployment
    new_issues = sentry.search_issues(
        query="is:unresolved firstSeen:>-30m",
        project="my-project"
    )

    if new_issues:
        print(f"⚠️  {len(new_issues)} NEW issues since deployment:\n")
        for issue in new_issues:
            print(f"  - {issue.get('title')}")

            # Get stack trace for first event
            events = sentry.get_events(issue.get("id"), limit=1)
            if events:
                trace = sentry.get_stacktrace(events[0]["id"])
                frames = trace.get("frames", [])[-3:]  # Last 3 frames
                for frame in frames:
                    print(f"      {frame.get('filename')}:{frame.get('lineno')}")
    else:
        print("✓ No new issues since deployment")
```

## Deep Investigation

```python
with SentrySession() as sentry:
    issue_id = "12345"

    # Get issue details
    issue = sentry.get_issue(issue_id)
    print(f"Investigating: {issue.get('title')}\n")
    print(f"  First seen: {issue.get('firstSeen')}")
    print(f"  Last seen: {issue.get('lastSeen')}")
    print(f"  Total occurrences: {issue.get('count')}")
    print(f"  Affected users: {issue.get('userCount')}\n")

    # Get recent events
    events = sentry.get_events(issue_id, limit=5)
    print("Recent events:")
    for event in events:
        print(f"  - {event.get('dateCreated')} | {event.get('user', {}).get('email', 'anonymous')}")

    # Get full stack trace
    if events:
        print("\nStack trace:")
        trace = sentry.get_stacktrace(events[0]["id"])
        for frame in trace.get("frames", []):
            if frame.get("inApp"):  # Only show app code
                print(f"  {frame.get('filename')}:{frame.get('lineno')}")
                print(f"    in {frame.get('function')}")
                if frame.get("context"):
                    print(f"    > {frame.get('contextLine', '').strip()}")

    # Trigger AI analysis
    print("\nRequesting AI analysis...")
    sentry.trigger_seer_analysis(issue_id)

    # Get recommendations
    recs = sentry.get_seer_recommendations(issue_id)
    if recs:
        print("\nAI Recommendations:")
        print(f"  Root cause: {recs.get('root_cause', 'Unknown')}")
        print(f"  Suggested fix: {recs.get('suggested_fix', 'None')}")
```

## Error Pattern Analysis

```python
with SentrySession() as sentry:
    # Find TypeError patterns
    typeErrors = sentry.search_issues(
        query="TypeError is:unresolved",
        project="my-project",
        limit=50
    )

    # Group by file
    by_file = {}
    for issue in typeErrors:
        # Get a sample event to find the file
        events = sentry.get_events(issue.get("id"), limit=1)
        if events:
            trace = sentry.get_stacktrace(events[0]["id"])
            frames = [f for f in trace.get("frames", []) if f.get("inApp")]
            if frames:
                filename = frames[-1].get("filename", "unknown")
                by_file.setdefault(filename, []).append(issue)

    print("TypeErrors by file:")
    for filename, issues in sorted(by_file.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"\n  {filename} ({len(issues)} issues)")
        for issue in issues[:3]:
            print(f"    - {issue.get('title')[:50]}")
```

## CLI Examples

```bash
# List your projects
python sentry_session.py --projects

# Search for errors
python sentry_session.py --search "is:unresolved level:error" --project my-project

# Get specific issue
python sentry_session.py --issue 12345

# Interactive session
python sentry_session.py --interactive
```

## Query Reference

| Query | Description |
|-------|-------------|
| `is:unresolved` | Open issues |
| `is:resolved` | Fixed issues |
| `level:error` | Error severity |
| `level:fatal` | Fatal/crash |
| `lastSeen:>-24h` | Active last 24h |
| `firstSeen:>-7d` | New this week |
| `user.email:foo@bar.com` | Specific user |
| `release:1.0.0` | Specific release |
| `environment:production` | Production env |
| `stack.filename:*views*` | File pattern |
