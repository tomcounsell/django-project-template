# MCP Development Guide

A standardized approach for building Model Context Protocol (MCP) servers in our Django application.

## Official Resources

**Primary Documentation:**
- [MCP Specification](https://modelcontextprotocol.io/docs)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) - Official Python implementation
- [FastMCP Documentation](https://github.com/modelcontextprotocol/python-sdk#fastmcp) - Simplified server API

**Version Tracking:**
- Python SDK: `mcp>=1.13.0` (in `pyproject.toml`)
- Update check: `uv add mcp --upgrade`

## Quick Start

### 1. Server Setup

All MCP servers live in `apps/{app_name}/mcp/server.py`:

```python
from mcp.server.fastmcp import FastMCP, Context

# Create server instance
mcp = FastMCP(
    "server-name",
    instructions="Brief description of server capabilities"
)
```

### 2. Register Tools (Functions AI Can Call)

```python
@mcp.tool()
def my_tool(param: str, optional: int = 10) -> dict[str, Any]:
    """Brief description shown to AI.

    Args:
        param: Parameter description
        optional: Optional parameter with default

    Returns:
        Dictionary with results
    """
    # Import Django models on-demand
    from apps.myapp.models import MyModel

    # Perform operation
    result = MyModel.objects.filter(field=param)[:optional]

    return {"results": [item.to_dict() for item in result]}
```

**With async and progress tracking:**

```python
@mcp.tool()
async def long_running_tool(param: str, ctx: Context) -> dict[str, Any]:
    """Tool that reports progress."""
    await ctx.info(f"Starting operation with {param}")

    # Do work...

    return {"status": "complete"}
```

### 3. Register Resources (Data Sources)

```python
@mcp.resource("myapp://items/{item_id}")
def get_item_details(item_id: str) -> str:
    """Get details about a specific item.

    Args:
        item_id: The item identifier

    Returns:
        Formatted string with item data
    """
    from apps.myapp.models import Item

    try:
        item = Item.objects.get(id=item_id)
        return f"Item: {item.name}\nStatus: {item.status}\n..."
    except Item.DoesNotExist:
        return f"Error: Item {item_id} not found"
```

### 4. Register Prompts (Pre-configured Templates)

```python
@mcp.prompt()
def analysis_prompt(item_id: str, depth: str = "brief") -> str:
    """Generate analysis prompt for an item.

    Args:
        item_id: Item to analyze
        depth: "brief" or "detailed"

    Returns:
        Formatted prompt string
    """
    if depth == "brief":
        return f"Provide a brief analysis of item {item_id}"
    return f"Provide detailed analysis of item {item_id} including history and trends"
```

## Django-Specific Patterns

### Import Models On-Demand

**Do this:**
```python
@mcp.tool()
def get_data(id: int):
    from apps.myapp.models import MyModel  # Import inside function
    return MyModel.objects.get(id=id)
```

**Not this:**
```python
from apps.myapp.models import MyModel  # Module-level import

@mcp.tool()
def get_data(id: int):
    return MyModel.objects.get(id=id)
```

**Why:** Avoid Django app registry issues and reduce startup overhead.

### Handle UUIDs Properly

```python
from uuid import UUID

@mcp.tool()
def get_by_uuid(id: str) -> dict:
    try:
        uuid_obj = UUID(id)  # Validate and convert
    except ValueError:
        return {"error": f"Invalid UUID format: {id}"}

    obj = MyModel.objects.get(id=uuid_obj)
    return {"id": str(obj.id), ...}  # Convert back to string
```

### Use Select/Prefetch for Performance

```python
@mcp.tool()
def get_with_relations(id: int):
    from apps.myapp.models import Parent

    obj = Parent.objects.select_related('user').prefetch_related('messages').get(id=id)
    return {"user": obj.user.username, "message_count": obj.messages.count()}
```

### Error Handling

```python
@mcp.tool()
def safe_tool(id: int) -> dict[str, Any]:
    """Tool with proper error handling."""
    from apps.myapp.models import MyModel

    try:
        obj = MyModel.objects.get(id=id)
        return {"success": True, "data": obj.to_dict()}
    except MyModel.DoesNotExist:
        return {"error": f"Object {id} not found"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}
```

## Testing

### Test Django Integration

```python
# In apps/myapp/tests/test_mcp.py
import pytest
from apps.myapp.mcp.server import mcp

@pytest.mark.django_db
def test_tool_with_database():
    """Test MCP tool interacts correctly with Django ORM."""
    # Setup test data
    obj = MyModel.objects.create(name="test")

    # Call tool
    result = mcp.call_tool("my_tool", {"id": obj.id})

    # Assert
    assert result["success"] is True
    assert result["name"] == "test"
```

### Test Without Database

```python
def test_tool_validation():
    """Test tool parameter validation."""
    result = mcp.call_tool("my_tool", {"id": "invalid"})
    assert "error" in result
```

## Running the Server

### Development

```bash
# With automatic reload
uv run mcp dev apps/myapp/mcp/server.py

# With Django settings
DJANGO_SETTINGS_MODULE=settings uv run mcp dev apps/myapp/mcp/server.py
```

### Testing with MCP Inspector

```bash
# Install inspector
npm install -g @modelcontextprotocol/inspector

# Run inspector
mcp-inspector uv run mcp dev apps/myapp/mcp/server.py
```

### Production (Stdio Transport)

```bash
DJANGO_SETTINGS_MODULE=settings python -m mcp run apps/myapp/mcp/server.py
```

## Integration with Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "django-myapp": {
      "command": "uv",
      "args": [
        "run",
        "--with", "mcp",
        "mcp", "run",
        "apps/myapp/mcp/server.py"
      ],
      "env": {
        "DJANGO_SETTINGS_MODULE": "settings"
      },
      "cwd": "/absolute/path/to/django-project-template"
    }
  }
}
```

Restart Claude Desktop after configuration changes.

## Best Practices

### 1. Naming Conventions

- **Server names:** `django-{app}-mcp` (e.g., `django-chat-mcp`)
- **Tool names:** Use snake_case verbs (e.g., `get_user_info`, `list_sessions`)
- **Resources:** Use URI schemes `{app}://{resource}/{param}` (e.g., `chat://sessions/123`)
- **Prompts:** End with `_prompt` (e.g., `analysis_prompt`)

### 2. Documentation

- **Always** include docstrings with Args/Returns sections
- Keep descriptions brief but informative (AI reads them)
- Use type hints for all parameters and returns

### 3. Response Format

**Structured (preferred):**
```python
return {"id": 123, "name": "value", "items": [...]}
```

**Text (for resources):**
```python
return "Formatted text\nWith newlines\nFor readability"
```

### 4. Security

- **Never** expose sensitive data (passwords, tokens, API keys)
- **Validate** all input parameters
- **Limit** query results (use `.[:limit]`)
- **Check permissions** before returning user-specific data

### 5. Performance

- Use `select_related()` and `prefetch_related()`
- Add `.only()` or `.defer()` for large models
- Set reasonable default limits (10-50 items)
- Consider caching for expensive operations

## File Structure

```
apps/
└── myapp/
    ├── mcp/
    │   ├── __init__.py
    │   ├── server.py         # Main MCP server
    │   └── README.md         # Usage instructions
    └── tests/
        └── test_mcp.py       # MCP server tests
```

## Troubleshooting

### Import Errors

**Problem:** `django.core.exceptions.AppRegistryNotReady`

**Solution:** Import models inside functions, not at module level.

### UUID Validation Errors

**Problem:** `ValueError: badly formed hexadecimal UUID string`

**Solution:** Wrap in try/except and validate with `UUID(string)`.

### Tool Not Showing in Claude

**Problem:** Tool defined but not appearing.

**Solution:**
1. Check decorator is `@mcp.tool()` (not `@mcp.tool`)
2. Restart Claude Desktop
3. Verify server starts without errors: `uv run mcp dev apps/myapp/mcp/server.py`

## Reference Implementation

See `apps/ai/mcp/server.py` for a complete working example with:
- 4 tools (user info, chat history, sessions, stats)
- 3 resources (session listings and details)
- 3 prompts (summaries, analysis, continuation)

## Version History

- **2025-10-02:** Initial guide (MCP SDK 1.13.0, FastMCP API)

## Related Documentation

- `apps/ai/mcp/README.md` - Chat MCP server documentation
- [MCP Quickstart](https://modelcontextprotocol.io/quickstart)
- [FastMCP Examples](https://github.com/modelcontextprotocol/python-sdk/tree/main/examples)
