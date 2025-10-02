# Django Chat MCP Server

This directory contains the Model Context Protocol (MCP) server implementation for the Django chat application.

## Overview

The MCP server provides AI assistants with access to the Django chat application's data and functionality through:

- **Tools**: Functions that can be called to perform operations
- **Resources**: Data sources that can be read
- **Prompts**: Pre-configured prompts for common tasks

## Running the Server

### Development Mode

```bash
# Using uv (recommended)
uv run mcp dev apps/ai/mcp/server.py

# Or using python directly
DJANGO_SETTINGS_MODULE=settings python -m mcp dev apps/ai/mcp/server.py
```

### Production Mode

```bash
# Using stdio transport
DJANGO_SETTINGS_MODULE=settings python -m mcp run apps/ai/mcp/server.py
```

## Available Tools

### `get_user_info(user_id: int)`
Retrieve information about a specific user.

**Example:**
```json
{
  "user_id": 1
}
```

### `get_chat_history(session_id: str, limit: int = 10)`
Get message history for a chat session.

**Example:**
```json
{
  "session_id": "123e4567-e89b-12d3-a456-426614174000",
  "limit": 20
}
```

### `list_user_sessions(user_id: int, limit: int = 20)`
List all chat sessions for a user.

**Example:**
```json
{
  "user_id": 1,
  "limit": 10
}
```

### `get_session_stats(session_id: str)`
Get detailed statistics about a chat session.

**Example:**
```json
{
  "session_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

## Available Resources

Resources use URI patterns and can be accessed by AI assistants to read data:

- `chat://sessions` - List recent chat sessions
- `chat://sessions/{session_id}` - Get details of a specific session
- `chat://users/{user_id}/sessions` - Get all sessions for a user

## Available Prompts

### `chat_summary_prompt(session_id: str, detail_level: str = "brief")`
Generate a prompt for summarizing a chat session.

### `user_analysis_prompt(user_id: str)`
Generate a prompt for analyzing a user's chat patterns.

### `conversation_continuation_prompt(session_id: str)`
Generate a prompt for continuing a conversation naturally.

## Integration with Claude Desktop

To use this server with Claude Desktop, add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "django-chat": {
      "command": "uv",
      "args": [
        "run",
        "--with",
        "mcp",
        "mcp",
        "run",
        "apps/ai/mcp/server.py"
      ],
      "env": {
        "DJANGO_SETTINGS_MODULE": "settings"
      },
      "cwd": "/path/to/django-project-template"
    }
  }
}
```

## Architecture

The server is built using FastMCP from the official `mcp` Python SDK. It:

- Uses decorator-based registration (`@mcp.tool()`, `@mcp.resource()`, `@mcp.prompt()`)
- Imports Django models on-demand to avoid startup overhead
- Handles UUID conversion for session IDs
- Provides type hints for all parameters
- Includes comprehensive docstrings

## Development

### Adding New Tools

```python
@mcp.tool()
def my_new_tool(param: str) -> dict[str, Any]:
    """Description of what the tool does.

    Args:
        param: Description of the parameter

    Returns:
        Description of the return value
    """
    # Implementation
    return {"result": "value"}
```

### Adding New Resources

```python
@mcp.resource("myapp://resource/{id}")
def get_my_resource(id: str) -> str:
    """Description of the resource.

    Args:
        id: The resource identifier

    Returns:
        Formatted string with resource data
    """
    # Implementation
    return "Resource data"
```

### Adding New Prompts

```python
@mcp.prompt()
def my_prompt_template(param: str) -> str:
    """Description of the prompt.

    Args:
        param: Description of the parameter

    Returns:
        Formatted prompt string
    """
    return f"Prompt template with {param}"
```

## Dependencies

- `mcp>=1.13.0` - Official MCP Python SDK
- Django ORM (for database queries)
- Python 3.11+

## See Also

- [MCP Specification](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [FastMCP Documentation](https://github.com/modelcontextprotocol/python-sdk#fastmcp)
