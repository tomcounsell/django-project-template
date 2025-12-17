# PostgreSQL Workflows

Common usage patterns for database inspection and analysis.

## Schema Documentation

```python
from postgres_session import PostgresSession

with PostgresSession() as db:
    # Get all tables with row counts
    tables = db.list_tables()

    print("Database Schema:\n")
    for table in tables:
        count = db.count(table)
        print(f"## {table} ({count:,} rows)\n")

        columns = db.describe_table(table)
        print("| Column | Type | Nullable | Default |")
        print("|--------|------|----------|---------|")
        for col in columns:
            nullable = "Yes" if col.get("is_nullable") == "YES" else "No"
            default = col.get("column_default", "-") or "-"
            print(f"| {col['column_name']} | {col['data_type']} | {nullable} | {default} |")
        print()
```

## Data Analysis

```python
with PostgresSession() as db:
    # User registration over time
    registrations = db.query("""
        SELECT
            DATE_TRUNC('month', date_joined) as month,
            COUNT(*) as new_users
        FROM auth_user
        GROUP BY 1
        ORDER BY 1 DESC
        LIMIT 12
    """)

    # Most active users
    active = db.query("""
        SELECT
            u.username,
            COUNT(s.id) as sessions
        FROM auth_user u
        LEFT JOIN django_session s ON s.session_data LIKE '%' || u.id || '%'
        GROUP BY u.id
        ORDER BY sessions DESC
        LIMIT 10
    """)
```

## Query Performance

```python
with PostgresSession() as db:
    # Analyze slow query
    plan = db.query("""
        EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
        SELECT * FROM large_table
        WHERE created_at > NOW() - INTERVAL '7 days'
    """)

    for row in plan:
        print(row.get("QUERY PLAN"))

    # Check missing indexes
    db.query("""
        SELECT
            schemaname,
            relname as table,
            seq_scan,
            seq_tup_read,
            idx_scan,
            idx_tup_fetch
        FROM pg_stat_user_tables
        WHERE seq_scan > idx_scan
        AND seq_tup_read > 10000
        ORDER BY seq_tup_read DESC
    """)
```

## Django-Specific Queries

```python
with PostgresSession() as db:
    # Recent migrations
    db.query("""
        SELECT app, name, applied
        FROM django_migrations
        ORDER BY applied DESC
        LIMIT 20
    """)

    # Content types
    db.query("""
        SELECT app_label, model, COUNT(*) as count
        FROM django_content_type ct
        LEFT JOIN auth_permission p ON p.content_type_id = ct.id
        GROUP BY ct.id
        ORDER BY count DESC
    """)

    # Check for orphaned sessions
    db.query("""
        SELECT COUNT(*) as expired_sessions
        FROM django_session
        WHERE expire_date < NOW()
    """)
```

## CLI Examples

```bash
# List all tables with counts
python postgres_session.py --tables

# Describe a table
python postgres_session.py --describe users

# Run a query
python postgres_session.py --sql "SELECT COUNT(*) FROM auth_user"

# Interactive mode
python postgres_session.py --interactive
```
