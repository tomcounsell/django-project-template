"""
Unit tests for MCP Skills framework.

These tests cover pure logic functions that don't require
MCP servers, databases, or network access.

Run with: pytest .claude/skills/_base/tests/ -v
"""

import os
import sys
import threading
from pathlib import Path
from unittest.mock import patch

import pytest

# Add skills directory to path for imports
skills_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(skills_dir / "_base" / "scripts"))

from mcp_session import MCPSession, check_required_env, load_env_files
from skill_generator import (
    categorize_tools,
    parse_mcp_source,
    to_kebab_case,
    to_snake_case,
)

# Also need PostgresSession for SQL tests
sys.path.insert(0, str(skills_dir / "postgres" / "scripts"))
from postgres_session import PostgresSession

# ============================================================
# Tests for to_snake_case
# ============================================================


class TestToSnakeCase:
    def test_kebab_case(self):
        assert to_snake_case("chrome-devtools") == "chrome_devtools"

    def test_camel_case(self):
        assert to_snake_case("mySkill") == "my_skill"

    def test_pascal_case(self):
        assert to_snake_case("MySkill") == "my_skill"

    def test_already_snake(self):
        assert to_snake_case("already_snake") == "already_snake"

    def test_spaces(self):
        assert to_snake_case("my skill name") == "my_skill_name"

    def test_mixed_separators(self):
        assert to_snake_case("my-skill_name") == "my_skill_name"

    def test_uppercase(self):
        assert to_snake_case("ALLCAPS") == "allcaps"

    def test_empty_string(self):
        assert to_snake_case("") == ""


# ============================================================
# Tests for to_kebab_case
# ============================================================


class TestToKebabCase:
    def test_snake_case(self):
        assert to_kebab_case("chrome_devtools") == "chrome-devtools"

    def test_camel_case(self):
        assert to_kebab_case("mySkill") == "my-skill"

    def test_pascal_case(self):
        assert to_kebab_case("MySkill") == "my-skill"

    def test_already_kebab(self):
        assert to_kebab_case("already-kebab") == "already-kebab"

    def test_spaces(self):
        assert to_kebab_case("my skill") == "my-skill"

    def test_empty_string(self):
        assert to_kebab_case("") == ""


# ============================================================
# Tests for parse_mcp_source
# ============================================================


class TestParseMcpSource:
    def test_npm_scoped_package(self):
        result = parse_mcp_source("@modelcontextprotocol/server-postgres")
        assert result["runtime"] == "npx"
        assert result["command"] == [
            "npx",
            "-y",
            "@modelcontextprotocol/server-postgres",
        ]
        assert (
            "server-postgres" not in result["package_name"]
            or result["package_name"] == ""
        )

    def test_npm_simple_package(self):
        result = parse_mcp_source("some-mcp-server")
        assert result["runtime"] == "npx"
        assert result["command"] == ["npx", "-y", "some-mcp-server"]
        assert result["package_name"] == "some-mcp-server"

    def test_npm_package_with_version(self):
        result = parse_mcp_source("@anthropic/mcp-server-chrome@0.1.0")
        assert result["runtime"] == "npx"
        assert "@0.1.0" in result["command"][2]

    def test_git_url(self):
        result = parse_mcp_source("git+https://github.com/org/mcp-postgres.git")
        assert result["runtime"] == "uvx"
        assert result["command"][0] == "uvx"

    def test_github_url(self):
        result = parse_mcp_source("https://github.com/org/mcp-server")
        assert result["runtime"] == "uvx"

    def test_http_url(self):
        result = parse_mcp_source("https://mcp.sentry.dev/sse")
        assert result["runtime"] == "http"
        assert result["command"] is None
        assert result["url"] == "https://mcp.sentry.dev/sse"

    def test_local_path_with_package_json(self, tmp_path):
        (tmp_path / "package.json").write_text(
            '{"name": "test-server", "main": "index.js"}'
        )
        result = parse_mcp_source(str(tmp_path))
        assert result["runtime"] == "node"
        assert result["package_name"] == "test-server"

    def test_local_path_with_pyproject(self, tmp_path):
        (tmp_path / "pyproject.toml").write_text("[project]\nname = 'test'")
        result = parse_mcp_source(str(tmp_path))
        assert result["runtime"] == "uvx"

    def test_invalid_source(self):
        with pytest.raises(ValueError, match="Could not determine"):
            parse_mcp_source("/nonexistent/path/to/nowhere")

    def test_whitespace_stripped(self):
        result = parse_mcp_source("  some-server  ")
        assert result["command"] == ["npx", "-y", "some-server"]


# ============================================================
# Tests for categorize_tools
# ============================================================


class TestCategorizeTools:
    def test_destructive_tools(self):
        tools = [{"name": "delete_user", "description": "Delete a user"}]
        result = categorize_tools(tools)
        assert "destructive" in result
        assert len(result["destructive"]) == 1

    def test_write_tools(self):
        tools = [{"name": "create_issue", "description": "Create an issue"}]
        result = categorize_tools(tools)
        assert "write" in result
        assert len(result["write"]) == 1

    def test_navigation_tools(self):
        tools = [{"name": "navigate_to", "description": "Navigate to URL"}]
        result = categorize_tools(tools)
        assert "navigation" in result

    def test_read_tools(self):
        tools = [{"name": "get_user", "description": "Get user info"}]
        result = categorize_tools(tools)
        assert "read" in result

    def test_utility_tools(self):
        tools = [{"name": "screenshot", "description": "Take a screenshot"}]
        result = categorize_tools(tools)
        assert "utility" in result

    def test_empty_categories_removed(self):
        tools = [{"name": "get_data", "description": ""}]
        result = categorize_tools(tools)
        assert "destructive" not in result
        assert "write" not in result

    def test_empty_tools_list(self):
        assert categorize_tools([]) == {}

    def test_mixed_tools(self):
        tools = [
            {"name": "get_user", "description": ""},
            {"name": "delete_user", "description": ""},
            {"name": "create_user", "description": ""},
        ]
        result = categorize_tools(tools)
        assert len(result["read"]) == 1
        assert len(result["destructive"]) == 1
        assert len(result["write"]) == 1


# ============================================================
# Tests for PostgresSession._is_read_only
# ============================================================


class TestIsReadOnly:
    """Test the SQL read-only checker."""

    def setup_method(self):
        self.session = PostgresSession.__new__(PostgresSession)

    # --- Allowed queries ---

    def test_select(self):
        assert self.session._is_read_only("SELECT * FROM users")

    def test_select_lowercase(self):
        assert self.session._is_read_only("select * from users")

    def test_select_mixed_case(self):
        assert self.session._is_read_only("Select id From users")

    def test_explain(self):
        assert self.session._is_read_only("EXPLAIN SELECT * FROM users")

    def test_show(self):
        assert self.session._is_read_only("SHOW search_path")

    def test_with_select(self):
        assert self.session._is_read_only("WITH cte AS (SELECT 1) SELECT * FROM cte")

    def test_leading_whitespace(self):
        assert self.session._is_read_only("  SELECT 1")

    # --- Forbidden queries ---

    def test_insert(self):
        assert not self.session._is_read_only("INSERT INTO users VALUES (1)")

    def test_update(self):
        assert not self.session._is_read_only("UPDATE users SET name = 'x'")

    def test_delete(self):
        assert not self.session._is_read_only("DELETE FROM users")

    def test_drop(self):
        assert not self.session._is_read_only("DROP TABLE users")

    def test_alter(self):
        assert not self.session._is_read_only("ALTER TABLE users ADD COLUMN x int")

    def test_create(self):
        assert not self.session._is_read_only("CREATE TABLE t (id int)")

    def test_truncate(self):
        assert not self.session._is_read_only("TRUNCATE users")

    def test_grant(self):
        assert not self.session._is_read_only("GRANT SELECT ON users TO role")

    def test_revoke(self):
        assert not self.session._is_read_only("REVOKE SELECT ON users FROM role")

    def test_copy(self):
        assert not self.session._is_read_only("COPY users TO STDOUT")

    def test_call(self):
        assert not self.session._is_read_only("CALL my_procedure()")

    def test_do_block(self):
        assert not self.session._is_read_only("DO $$ BEGIN DELETE FROM users; END $$")

    # --- Bypass attempts ---

    def test_semicolon_injection(self):
        assert not self.session._is_read_only("SELECT 1; DROP TABLE users")

    def test_semicolon_insert(self):
        assert not self.session._is_read_only("SELECT 1; INSERT INTO t VALUES (1)")

    # --- Edge cases ---

    def test_empty_string(self):
        assert not self.session._is_read_only("")

    def test_whitespace_only(self):
        assert not self.session._is_read_only("   ")

    def test_unknown_statement(self):
        assert not self.session._is_read_only("VACUUM users")


# ============================================================
# Tests for check_required_env
# ============================================================


class TestCheckRequiredEnv:
    def test_all_present(self):
        with patch.dict(os.environ, {"KEY1": "val1", "KEY2": "val2"}):
            check_required_env(["KEY1", "KEY2"])  # Should not raise

    def test_missing_raises(self):
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(EnvironmentError, match="MISSING_KEY"):
                check_required_env(["MISSING_KEY"])

    def test_empty_list(self):
        check_required_env([])  # Should not raise


# ============================================================
# Tests for load_env_files
# ============================================================


class TestLoadEnvFiles:
    def test_loads_from_existing_file(self, tmp_path):
        env_file = tmp_path / ".env"
        env_file.write_text("TEST_MCP_VAR=hello_world\n")

        # Clean up after test
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("TEST_MCP_VAR", None)
            load_env_files([env_file])
            assert os.environ.get("TEST_MCP_VAR") == "hello_world"

    def test_does_not_override_existing(self, tmp_path):
        env_file = tmp_path / ".env"
        env_file.write_text("TEST_MCP_EXISTING=new_value\n")

        with patch.dict(os.environ, {"TEST_MCP_EXISTING": "original"}, clear=False):
            load_env_files([env_file])
            assert os.environ.get("TEST_MCP_EXISTING") == "original"

    def test_skips_nonexistent_files(self):
        load_env_files([Path("/nonexistent/.env")])  # Should not raise


# ============================================================
# Tests for MCPSession thread safety
# ============================================================


class TestMCPSessionThreadSafety:
    def test_responses_lock_exists(self):
        session = MCPSession()
        assert hasattr(session, "_responses_lock")
        assert isinstance(session._responses_lock, type(threading.Lock()))

    def test_responses_dict_initialized(self):
        session = MCPSession()
        assert session.responses == {}
