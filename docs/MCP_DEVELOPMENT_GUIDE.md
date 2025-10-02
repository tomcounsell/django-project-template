# MCP Development Guide

Standardized approach for building Model Context Protocol servers in Django apps.

## Official Documentation

**Read these first:**
- [MCP Quickstart](https://modelcontextprotocol.io/quickstart) - Core concepts
- [Python SDK README](https://github.com/modelcontextprotocol/python-sdk#quickstart) - API reference
- [FastMCP Section](https://github.com/modelcontextprotocol/python-sdk#fastmcp) - Decorator API

**Version:**
- Current: `mcp>=1.13.0` (see `pyproject.toml`)
- Update: `uv add mcp --upgrade`

## Django-Specific Patterns

### Import Models On-Demand

**Always import Django models inside functions**, not at module level:

```python
@mcp.tool()
def get_data(id: int):
    from apps.myapp.models import MyModel  # ✅ Import here
    return MyModel.objects.get(id=id)
```

**Why:** Avoids Django app registry issues when MCP server loads.

### Handle UUID Fields

```python
from uuid import UUID

@mcp.tool()
def get_session(session_id: str):
    try:
        uuid_obj = UUID(session_id)  # Validate format
    except ValueError:
        return {"error": f"Invalid UUID: {session_id}"}

    from apps.ai.models import ChatSession
    session = ChatSession.objects.get(id=uuid_obj)
    return {"id": str(session.id), ...}  # Convert back to string
```

### Query Optimization

Use Django ORM optimizations to avoid N+1 queries:

```python
@mcp.tool()
def list_items(limit: int = 20):
    from apps.myapp.models import Item

    items = (
        Item.objects
        .select_related('user')           # For ForeignKey
        .prefetch_related('messages')     # For reverse FK/M2M
        .only('id', 'name', 'status')     # Limit fields
        [:limit]                          # Always limit results
    )
    return [item.to_dict() for item in items]
```

## Project Conventions

### File Structure

```
apps/
└── {app_name}/
    ├── mcp/
    │   ├── __init__.py
    │   ├── server.py      # MCP server implementation
    │   └── README.md      # App-specific usage docs
    └── tests/
        └── test_mcp.py    # MCP server tests
```

### Naming Standards

- **Server:** `django-{app}-mcp` (e.g., `django-chat-mcp`)
- **Tools:** Snake_case verbs (e.g., `get_user_info`, `list_sessions`)
- **Resources:** URI scheme `{app}://{resource}` (e.g., `chat://sessions/123`)
- **Prompts:** End with `_prompt` (e.g., `analysis_prompt`)

### Security

- Never expose passwords, tokens, or API keys
- Validate all input parameters
- Always limit query results (default: 10-50 items)
- Check user permissions before returning data

## Running Servers

### Development

```bash
DJANGO_SETTINGS_MODULE=settings uv run mcp dev apps/{app}/mcp/server.py
```

### Claude Desktop Integration

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "django-{app}": {
      "command": "uv",
      "args": ["run", "--with", "mcp", "mcp", "run", "apps/{app}/mcp/server.py"],
      "env": {"DJANGO_SETTINGS_MODULE": "settings"},
      "cwd": "/absolute/path/to/project"
    }
  }
}
```

Restart Claude Desktop after changes.

## Testing

```python
# apps/myapp/tests/test_mcp.py
import pytest
from apps.myapp.mcp.server import mcp

@pytest.mark.django_db
def test_tool_with_database():
    from apps.myapp.models import MyModel

    obj = MyModel.objects.create(name="test")
    result = mcp.call_tool("my_tool", {"id": obj.id})

    assert result["success"] is True
```

## Troubleshooting

**`AppRegistryNotReady` error:**
- Import models inside functions, not at module level

**Tool not appearing in Claude:**
1. Verify decorator has parentheses: `@mcp.tool()` not `@mcp.tool`
2. Restart Claude Desktop
3. Check server starts: `uv run mcp dev apps/{app}/mcp/server.py`

**UUID validation errors:**
- Always validate UUIDs: `uuid_obj = UUID(string_param)`
- Wrap in try/except for user-friendly errors

## Reference Implementation

See `apps/ai/mcp/server.py` for complete working example with:
- 4 tools, 3 resources, 3 prompts
- Django ORM integration patterns
- Error handling examples
- UUID validation

## Version History

- **2025-10-02:** Initial guide (MCP SDK 1.13.0)
