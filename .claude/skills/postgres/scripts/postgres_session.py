#!/usr/bin/env python3
"""
PostgreSQL MCP Skill Session

Query and inspect PostgreSQL databases with read-only safety.
"""

import json
import re
import sys
from pathlib import Path

# Import base session
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "_base" / "scripts"))
from mcp_session import MCPSession


class PostgresSession(MCPSession):
    """Session manager for PostgreSQL MCP skill."""

    MCP_COMMAND = ["npx", "-y", "@modelcontextprotocol/server-postgres@latest"]
    REQUIRED_ENV = ["DATABASE_URL"]
    OPTIONAL_ENV = []

    # Read-only SQL patterns
    ALLOWED_PATTERNS = [
        r"^\s*SELECT\b",
        r"^\s*EXPLAIN\b",
        r"^\s*SHOW\b",
        r"^\s*WITH\b.*\bSELECT\b",
        r"^\s*\\d",  # psql describe commands
    ]

    FORBIDDEN_PATTERNS = [
        r"\bINSERT\b",
        r"\bUPDATE\b",
        r"\bDELETE\b",
        r"\bDROP\b",
        r"\bALTER\b",
        r"\bCREATE\b",
        r"\bTRUNCATE\b",
        r"\bGRANT\b",
        r"\bREVOKE\b",
    ]

    def _is_read_only(self, sql: str) -> bool:
        """Check if SQL is read-only."""
        sql_upper = sql.upper()

        # Check for forbidden operations
        for pattern in self.FORBIDDEN_PATTERNS:
            if re.search(pattern, sql_upper):
                return False

        # Check for allowed operations
        for pattern in self.ALLOWED_PATTERNS:
            if re.search(pattern, sql_upper, re.IGNORECASE):
                return True

        return False

    def query(self, sql: str) -> list | dict:
        """
        Execute a read-only SQL query.

        Args:
            sql: SQL query to execute (must be read-only)

        Returns:
            Query results as list of dicts

        Raises:
            ValueError: If query is not read-only
        """
        if not self._is_read_only(sql):
            raise ValueError(
                "Only read-only queries (SELECT, EXPLAIN, SHOW) are allowed. "
                "This is a safety feature to prevent accidental data modification."
            )

        return self.call_tool("query", {"sql": sql})

    def list_tables(self) -> list[str]:
        """Get list of tables in public schema."""
        result = self.query("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        return [row.get("table_name") for row in result] if isinstance(result, list) else []

    def describe_table(self, table_name: str) -> list[dict]:
        """Get column information for a table."""
        # Sanitize table name
        if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", table_name):
            raise ValueError(f"Invalid table name: {table_name}")

        return self.query(f"""
            SELECT
                column_name,
                data_type,
                is_nullable,
                column_default,
                character_maximum_length
            FROM information_schema.columns
            WHERE table_name = '{table_name}'
            ORDER BY ordinal_position
        """)

    def count(self, table_name: str) -> int:
        """Get row count for a table."""
        if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", table_name):
            raise ValueError(f"Invalid table name: {table_name}")

        result = self.query(f"SELECT COUNT(*) as count FROM {table_name}")
        if isinstance(result, list) and result:
            return result[0].get("count", 0)
        return 0


def main():
    """CLI interface for PostgreSQL skill."""
    import argparse

    parser = argparse.ArgumentParser(description="PostgreSQL MCP Skill")
    parser.add_argument("--sql", help="SQL query to execute")
    parser.add_argument("--tables", action="store_true", help="List all tables")
    parser.add_argument("--describe", help="Describe a table")
    parser.add_argument("--interactive", action="store_true", help="Interactive SQL mode")

    args = parser.parse_args()

    with PostgresSession() as db:
        if args.tables:
            tables = db.list_tables()
            print("Tables:")
            for table in tables:
                count = db.count(table)
                print(f"  {table} ({count} rows)")
            return

        if args.describe:
            columns = db.describe_table(args.describe)
            print(f"Table: {args.describe}")
            for col in columns:
                nullable = "NULL" if col.get("is_nullable") == "YES" else "NOT NULL"
                default = f" DEFAULT {col.get('column_default')}" if col.get("column_default") else ""
                print(f"  {col.get('column_name')}: {col.get('data_type')} {nullable}{default}")
            return

        if args.sql:
            result = db.query(args.sql)
            print(json.dumps(result, indent=2, default=str))
            return

        if args.interactive:
            print("PostgreSQL Interactive Mode")
            print("Type SQL queries (read-only). Commands: \\dt (tables), \\d table (describe), \\q (quit)")
            print()

            while True:
                try:
                    sql = input("sql> ").strip()
                except (EOFError, KeyboardInterrupt):
                    break

                if not sql:
                    continue

                if sql in ("\\q", "quit", "exit"):
                    break

                if sql == "\\dt":
                    tables = db.list_tables()
                    for table in tables:
                        print(f"  {table}")
                    continue

                if sql.startswith("\\d "):
                    table = sql[3:].strip()
                    try:
                        columns = db.describe_table(table)
                        for col in columns:
                            print(f"  {col.get('column_name')}: {col.get('data_type')}")
                    except Exception as e:
                        print(f"Error: {e}")
                    continue

                try:
                    result = db.query(sql)
                    if isinstance(result, list):
                        for row in result[:20]:  # Limit output
                            print(row)
                        if len(result) > 20:
                            print(f"... and {len(result) - 20} more rows")
                    else:
                        print(result)
                except Exception as e:
                    print(f"Error: {e}")

            return

        parser.print_help()


if __name__ == "__main__":
    main()
