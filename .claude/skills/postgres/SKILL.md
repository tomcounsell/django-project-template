---
name: postgres
description: Query and inspect PostgreSQL databases
triggers:
  - "query the database"
  - "database schema"
  - "SQL query"
  - "check the database"
  - "table structure"
  - "database tables"
  - "run SQL"
mcp_source: "@modelcontextprotocol/server-postgres"
---

# PostgreSQL Skill

Query and inspect PostgreSQL databases directly from Claude Code.

## Overview

This skill provides read-only access to PostgreSQL databases for:
- Schema exploration and documentation
- Data analysis and debugging
- Query testing and optimization
- Understanding database structure

## Required Environment Variables

- `DATABASE_URL` - PostgreSQL connection string

Set in `~/.env/services/.env` or `.env.local`:
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
```

## Available Tools

### Query Operations (1 tool)
- **query** - Execute a read-only SQL query and return results

## Usage

### Basic Query

```python
from postgres_session import PostgresSession

with PostgresSession() as db:
    # Simple query
    users = db.query("SELECT * FROM users LIMIT 10")
    print(users)

    # Get table list
    tables = db.query("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        ORDER BY table_name
    """)
```

### Schema Exploration

```python
with PostgresSession() as db:
    # List all tables
    tables = db.query("""
        SELECT table_name, pg_size_pretty(pg_total_relation_size(quote_ident(table_name)))
        FROM information_schema.tables
        WHERE table_schema = 'public'
    """)

    # Get columns for a table
    columns = db.query("""
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns
        WHERE table_name = 'users'
        ORDER BY ordinal_position
    """)

    # Find foreign keys
    fks = db.query("""
        SELECT
            tc.table_name,
            kcu.column_name,
            ccu.table_name AS foreign_table,
            ccu.column_name AS foreign_column
        FROM information_schema.table_constraints AS tc
        JOIN information_schema.key_column_usage AS kcu
            ON tc.constraint_name = kcu.constraint_name
        JOIN information_schema.constraint_column_usage AS ccu
            ON ccu.constraint_name = tc.constraint_name
        WHERE tc.constraint_type = 'FOREIGN KEY'
    """)
```

### Query Analysis

```python
with PostgresSession() as db:
    # Explain a query
    plan = db.query("""
        EXPLAIN ANALYZE
        SELECT u.*, COUNT(o.id) as order_count
        FROM users u
        LEFT JOIN orders o ON o.user_id = u.id
        GROUP BY u.id
    """)

    # Check indexes
    indexes = db.query("""
        SELECT indexname, indexdef
        FROM pg_indexes
        WHERE tablename = 'users'
    """)
```

## CLI Usage

```bash
# Interactive SQL session
python postgres_session.py --interactive

# Run a single query
python postgres_session.py --sql "SELECT COUNT(*) FROM users"

# List tables
python postgres_session.py --sql "SELECT table_name FROM information_schema.tables WHERE table_schema='public'"
```

## Safety

This skill enforces **read-only** queries:
- Only SELECT, EXPLAIN, and SHOW statements allowed
- No INSERT, UPDATE, DELETE, DROP, or ALTER
- Connection uses read-only transaction mode when possible

## Django Integration

For Django projects, use the same DATABASE_URL from your `.env.local`:

```python
# The skill automatically loads from .env.local
# which should have:
# DATABASE_URL=postgres://user@localhost:5432/django-project-template
```

## Common Queries for Django

```python
with PostgresSession() as db:
    # List Django migrations
    migrations = db.query("""
        SELECT app, name, applied
        FROM django_migrations
        ORDER BY applied DESC
        LIMIT 20
    """)

    # Check Django sessions
    sessions = db.query("""
        SELECT COUNT(*), MAX(expire_date)
        FROM django_session
    """)

    # Analyze user table
    db.query("SELECT COUNT(*) FROM auth_user")
```
