#!/usr/bin/env python3
"""
MCP Skill Generator

Generates a complete skill directory structure from an MCP server source.

Usage:
    python skill_generator.py --source "@modelcontextprotocol/server-postgres" \
        --name "postgres" --description "Query PostgreSQL databases"
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from textwrap import dedent

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))
from mcp_session import introspect_mcp_server


def parse_mcp_source(source: str) -> dict:
    """
    Parse an MCP source string and determine the runtime.

    Returns:
        dict with 'command', 'runtime', 'package_name'
    """
    source = source.strip()

    # npm package (starts with @ or is a simple package name)
    if source.startswith("@") or (
        not source.startswith(("http", "git+", "/", "~", "."))
        and "/" not in source
    ):
        package = source
        if not package.endswith("@latest"):
            package = f"{package}@latest"
        return {
            "command": ["npx", "-y", package],
            "runtime": "npx",
            "package_name": source.split("@")[0] if source.startswith("@") else source,
        }

    # Git URL
    if source.startswith("git+") or (
        source.startswith("https://github.com") and not source.endswith(".git")
    ):
        url = source
        if source.startswith("https://github.com") and not source.startswith("git+"):
            url = f"git+{source}"
        # Extract command name from repo
        repo_name = source.split("/")[-1].replace(".git", "")
        cmd_name = repo_name.replace("mcp-", "").replace("-mcp", "")
        return {
            "command": ["uvx", "--from", url, cmd_name],
            "runtime": "uvx",
            "package_name": repo_name,
        }

    # HTTP URL (remote MCP server)
    if source.startswith("http://") or source.startswith("https://"):
        return {
            "command": None,  # HTTP sessions don't use subprocess
            "runtime": "http",
            "package_name": source.split("//")[1].split("/")[0],
            "url": source,
        }

    # Local path
    local_path = Path(source).expanduser().resolve()
    if local_path.exists():
        # Check for package.json (Node.js)
        if (local_path / "package.json").exists():
            with open(local_path / "package.json") as f:
                pkg = json.load(f)
            main = pkg.get("main", "index.js")
            return {
                "command": ["node", str(local_path / main)],
                "runtime": "node",
                "package_name": pkg.get("name", local_path.name),
            }
        # Check for pyproject.toml (Python)
        if (local_path / "pyproject.toml").exists():
            return {
                "command": ["uvx", "--from", str(local_path), local_path.name],
                "runtime": "uvx",
                "package_name": local_path.name,
            }

    raise ValueError(f"Could not determine MCP runtime for source: {source}")


def to_snake_case(name: str) -> str:
    """Convert kebab-case or other formats to snake_case."""
    # Replace hyphens and spaces with underscores
    name = re.sub(r"[-\s]+", "_", name)
    # Insert underscores before uppercase letters
    name = re.sub(r"([a-z])([A-Z])", r"\1_\2", name)
    return name.lower()


def to_kebab_case(name: str) -> str:
    """Convert to kebab-case for directory names."""
    name = re.sub(r"[_\s]+", "-", name)
    name = re.sub(r"([a-z])([A-Z])", r"\1-\2", name)
    return name.lower()


def categorize_tools(tools: list[dict]) -> dict[str, list[dict]]:
    """Categorize tools by their likely operation type."""
    categories = {
        "read": [],
        "write": [],
        "navigation": [],
        "destructive": [],
        "utility": [],
    }

    for tool in tools:
        name = tool.get("name", "").lower()
        desc = tool.get("description", "").lower()

        if any(
            word in name
            for word in ["delete", "remove", "drop", "purge", "destroy", "clear"]
        ):
            categories["destructive"].append(tool)
        elif any(
            word in name for word in ["create", "insert", "add", "update", "set", "put"]
        ):
            categories["write"].append(tool)
        elif any(
            word in name for word in ["navigate", "goto", "open", "click", "scroll"]
        ):
            categories["navigation"].append(tool)
        elif any(
            word in name for word in ["get", "list", "query", "search", "find", "read"]
        ):
            categories["read"].append(tool)
        else:
            categories["utility"].append(tool)

    # Remove empty categories
    return {k: v for k, v in categories.items() if v}


def generate_skill_md(
    name: str,
    description: str,
    server_info: dict,
    tools: list[dict],
    mcp_source: str,
    required_env: list[str],
) -> str:
    """Generate the SKILL.md content."""
    categories = categorize_tools(tools)
    snake_name = to_snake_case(name)

    # Build tool documentation
    tool_docs = []
    for category, category_tools in categories.items():
        tool_docs.append(f"\n### {category.title()} Operations ({len(category_tools)} tools)\n")
        for tool in category_tools:
            tool_name = tool.get("name", "unknown")
            tool_desc = tool.get("description", "No description")
            # Truncate long descriptions
            if len(tool_desc) > 100:
                tool_desc = tool_desc[:97] + "..."
            tool_docs.append(f"- **{tool_name}** - {tool_desc}")

    tool_section = "\n".join(tool_docs)

    # Build env var section
    env_section = ""
    if required_env:
        env_lines = [f"- `{var}`" for var in required_env]
        env_section = f"""
## Required Environment Variables

{chr(10).join(env_lines)}

Set these in `~/.env/services/.env` or `.env.local`
"""

    return dedent(f'''
---
name: {name}
description: {description}
triggers:
  - "{name}"
  - "{description.lower()}"
mcp_source: "{mcp_source}"
---

# {name.replace("-", " ").title()} Skill

{description}

## Overview

This skill wraps the **{server_info.get("name", "MCP Server")}** MCP server, providing
{len(tools)} tools for integration with Claude Code.

## Architecture

```
┌─────────────────┐     stdin/stdout      ┌─────────────────┐
│  Claude Code    │ ◄──── JSON-RPC ─────► │  MCP Server     │
│  (skill script) │                       │  (subprocess)   │
└─────────────────┘                       └─────────────────┘
```
{env_section}
## Available Tools

Total: {len(tools)} tools
{tool_section}

## Usage

### Starting a Session

```python
from {snake_name}_session import {snake_name.title().replace("_", "")}Session

# Using context manager (recommended)
with {snake_name.title().replace("_", "")}Session() as session:
    result = session.call_tool("tool_name", {{"arg": "value"}})
    print(result)

# Manual management
session = {snake_name.title().replace("_", "")}Session()
session.start()
try:
    result = session.call_tool("tool_name", {{"arg": "value"}})
finally:
    session.stop()
```

### Listing Available Tools

```python
with {snake_name.title().replace("_", "")}Session() as session:
    for tool in session.list_tools():
        print(f"{{tool['name']}}: {{tool.get('description', '')}}")
```

## Tool Reference

See the full tool schemas in `scripts/tool_schemas.json`.
''').strip()


def generate_session_script(
    name: str,
    mcp_command: list[str],
    required_env: list[str],
    optional_env: list[str],
) -> str:
    """Generate the session script for this skill."""
    snake_name = to_snake_case(name)
    class_name = "".join(word.title() for word in snake_name.split("_")) + "Session"
    command_str = json.dumps(mcp_command)
    required_str = json.dumps(required_env)
    optional_str = json.dumps(optional_env)

    return dedent(f'''
#!/usr/bin/env python3
"""
{name.replace("-", " ").title()} MCP Skill Session

Auto-generated session manager for the {name} skill.
"""

import json
import sys
from pathlib import Path

# Import base session
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "_base" / "scripts"))
from mcp_session import MCPSession


class {class_name}(MCPSession):
    """Session manager for {name} MCP skill."""

    MCP_COMMAND = {command_str}
    REQUIRED_ENV = {required_str}
    OPTIONAL_ENV = {optional_str}


def main():
    """CLI interface for the skill session."""
    import argparse

    parser = argparse.ArgumentParser(description="{name.replace('-', ' ').title()} MCP Skill")
    parser.add_argument("--list-tools", action="store_true", help="List available tools")
    parser.add_argument("--tool", help="Tool name to call")
    parser.add_argument("--args", help="Tool arguments as JSON string")
    parser.add_argument("--interactive", action="store_true", help="Interactive mode")

    args = parser.parse_args()

    with {class_name}() as session:
        if args.list_tools:
            print("Available tools:")
            for tool in session.list_tools():
                print(f"  - {{tool['name']}}: {{tool.get('description', '')[:60]}}")
            return

        if args.tool:
            tool_args = {{}}
            if args.args:
                tool_args = json.loads(args.args)
            result = session.call_tool(args.tool, tool_args)
            print(json.dumps(result, indent=2))
            return

        if args.interactive:
            print(f"{{len(session.tools)}} tools available. Type 'help' for commands.")
            while True:
                try:
                    cmd = input("> ").strip()
                except (EOFError, KeyboardInterrupt):
                    break

                if not cmd:
                    continue
                if cmd == "help":
                    print("Commands: list, call <tool> [json_args], quit")
                elif cmd == "list":
                    for tool in session.list_tools():
                        print(f"  {{tool['name']}}")
                elif cmd.startswith("call "):
                    parts = cmd[5:].split(" ", 1)
                    tool_name = parts[0]
                    tool_args = {{}}
                    if len(parts) > 1:
                        tool_args = json.loads(parts[1])
                    result = session.call_tool(tool_name, tool_args)
                    print(json.dumps(result, indent=2))
                elif cmd in ("quit", "exit"):
                    break
            return

        parser.print_help()


if __name__ == "__main__":
    main()
''').strip()


def generate_workflows_md(name: str, tools: list[dict]) -> str:
    """Generate example workflows documentation."""
    snake_name = to_snake_case(name)
    class_name = "".join(word.title() for word in snake_name.split("_")) + "Session"

    # Pick a few representative tools for examples
    example_tools = tools[:3] if len(tools) >= 3 else tools

    examples = []
    for i, tool in enumerate(example_tools, 1):
        tool_name = tool.get("name", "unknown")
        tool_desc = tool.get("description", "No description")
        schema = tool.get("inputSchema", {})
        properties = schema.get("properties", {})

        # Build example args
        example_args = {}
        for prop_name, prop_schema in list(properties.items())[:2]:
            prop_type = prop_schema.get("type", "string")
            if prop_type == "string":
                example_args[prop_name] = f"example_{prop_name}"
            elif prop_type == "number" or prop_type == "integer":
                example_args[prop_name] = 1
            elif prop_type == "boolean":
                example_args[prop_name] = True

        examples.append(f"""
### Example {i}: {tool_name}

**Description:** {tool_desc}

```python
result = session.call_tool("{tool_name}", {json.dumps(example_args, indent=4)})
```
""")

    return dedent(f'''
# {name.replace("-", " ").title()} Workflows

Common usage patterns for the {name} skill.

## Basic Usage

```python
from {snake_name}_session import {class_name}

with {class_name}() as session:
    # Your workflow here
    pass
```

## Example Workflows
{"".join(examples)}

## CLI Usage

```bash
# List available tools
python {snake_name}_session.py --list-tools

# Call a tool
python {snake_name}_session.py --tool tool_name --args '{{"arg": "value"}}'

# Interactive mode
python {snake_name}_session.py --interactive
```
''').strip()


def generate_skill(
    source: str,
    name: str,
    description: str,
    required_env: list[str] | None = None,
    optional_env: list[str] | None = None,
    output_dir: Path | None = None,
    env_vars: dict | None = None,
) -> Path:
    """
    Generate a complete skill directory from an MCP source.

    Args:
        source: MCP server source (npm package, git URL, local path)
        name: Skill name (kebab-case)
        description: Brief skill description
        required_env: Required environment variables
        optional_env: Optional environment variables
        output_dir: Output directory (defaults to .claude/skills/)
        env_vars: Environment variables to set for introspection

    Returns:
        Path to the generated skill directory
    """
    required_env = required_env or []
    optional_env = optional_env or []

    # Parse the source
    parsed = parse_mcp_source(source)
    mcp_command = parsed["command"]

    if mcp_command is None:
        raise NotImplementedError("HTTP MCP servers not yet supported")

    # Set any provided env vars
    if env_vars:
        for key, value in env_vars.items():
            os.environ[key] = value

    # Introspect the server
    print(f"Introspecting MCP server: {' '.join(mcp_command)}")
    result = introspect_mcp_server(mcp_command, env_vars)
    server_info = result["server_info"]
    tools = result["tools"]

    print(f"Found {len(tools)} tools from {server_info.get('name', 'Unknown')}")

    # Determine output directory
    if output_dir is None:
        # Try to find .claude/skills in current or parent directories
        current = Path.cwd()
        while current != current.parent:
            skills_dir = current / ".claude" / "skills"
            if skills_dir.exists() or (current / ".claude").exists():
                output_dir = skills_dir
                break
            current = current.parent
        if output_dir is None:
            output_dir = Path.cwd() / ".claude" / "skills"

    # Create skill directory
    skill_name = to_kebab_case(name)
    skill_dir = output_dir / skill_name
    scripts_dir = skill_dir / "scripts"
    examples_dir = skill_dir / "examples"

    skill_dir.mkdir(parents=True, exist_ok=True)
    scripts_dir.mkdir(exist_ok=True)
    examples_dir.mkdir(exist_ok=True)

    # Generate files
    skill_md = generate_skill_md(
        name=skill_name,
        description=description,
        server_info=server_info,
        tools=tools,
        mcp_source=source,
        required_env=required_env,
    )

    session_script = generate_session_script(
        name=skill_name,
        mcp_command=mcp_command,
        required_env=required_env,
        optional_env=optional_env,
    )

    workflows_md = generate_workflows_md(name=skill_name, tools=tools)

    # Write files
    (skill_dir / "SKILL.md").write_text(skill_md)
    print(f"  Created: {skill_dir / 'SKILL.md'}")

    snake_name = to_snake_case(skill_name)
    session_path = scripts_dir / f"{snake_name}_session.py"
    session_path.write_text(session_script)
    session_path.chmod(0o755)
    print(f"  Created: {session_path}")

    (examples_dir / "workflows.md").write_text(workflows_md)
    print(f"  Created: {examples_dir / 'workflows.md'}")

    # Save tool schemas
    schemas_path = scripts_dir / "tool_schemas.json"
    schemas_path.write_text(json.dumps(tools, indent=2))
    print(f"  Created: {schemas_path}")

    print(f"\nSkill '{skill_name}' generated at: {skill_dir}")
    return skill_dir


def main():
    parser = argparse.ArgumentParser(
        description="Generate an MCP skill from a server source",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=dedent("""
        Examples:
            # npm package
            python skill_generator.py --source "@modelcontextprotocol/server-postgres" \\
                --name postgres --description "Query PostgreSQL databases"

            # Git repository
            python skill_generator.py --source "git+https://github.com/anthropics/mcp-server-example" \\
                --name example --description "Example MCP skill"

            # With required env vars
            python skill_generator.py --source "@sentry/mcp-server" \\
                --name sentry --description "Sentry error tracking" \\
                --env SENTRY_AUTH_TOKEN
        """),
    )
    parser.add_argument(
        "--source",
        required=True,
        help="MCP server source (npm package, git URL, or local path)",
    )
    parser.add_argument(
        "--name",
        required=True,
        help="Skill name (kebab-case)",
    )
    parser.add_argument(
        "--description",
        required=True,
        help="Brief skill description",
    )
    parser.add_argument(
        "--env",
        action="append",
        default=[],
        dest="required_env",
        help="Required environment variable (can specify multiple)",
    )
    parser.add_argument(
        "--optional-env",
        action="append",
        default=[],
        help="Optional environment variable (can specify multiple)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output directory (defaults to .claude/skills/)",
    )

    args = parser.parse_args()

    try:
        generate_skill(
            source=args.source,
            name=args.name,
            description=args.description,
            required_env=args.required_env,
            optional_env=args.optional_env,
            output_dir=args.output,
        )
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
