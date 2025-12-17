# MCP Skills Framework

A pattern for wrapping Model Context Protocol (MCP) servers as Claude Code skills with persistent session management and automatic tool discovery.

## Table of Contents

- [Overview](#overview)
- [Why MCP Skills?](#why-mcp-skills)
- [Quick Start](#quick-start)
- [Creating Skills](#creating-skills)
- [Skill Architecture](#skill-architecture)
- [Session Management Patterns](#session-management-patterns)
- [Best Practices](#best-practices)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)

---

## Overview

MCP skills provide a standardized way to integrate external tools and services into Claude Code workflows. Instead of manually configuring MCP servers or writing one-off integration scripts, this framework:

- **Auto-discovers** MCP server capabilities via `tools/list`
- **Generates** complete skill directories with session scripts, documentation, and examples
- **Manages** persistent subprocess sessions for stateful operations
- **Standardizes** JSON-RPC communication over stdin/stdout

### What Gets Generated

Each skill is a self-contained directory under `.claude/skills/`:

```
.claude/skills/
└── {skill-name}/
    ├── SKILL.md                      # Skill definition with tool docs
    ├── scripts/
    │   ├── {skill_name}_session.py   # Persistent session manager
    │   └── introspect_tools.py       # Tool discovery utility
    └── examples/
        └── workflows.md              # Common usage patterns
```

---

## Why MCP Skills?

### Problem: Context Switching

**Before MCP skills**, investigating a production error requires:
1. Open Sentry in browser
2. Search for error manually
3. Copy stack trace
4. Switch back to Claude
5. Paste and explain context

**With MCP skills**, Claude handles it directly:
```
User: "Check for TypeError issues in the checkout flow"
Claude: [Uses sentry skill → searches issues → analyzes traces → suggests fixes]
```

### Key Benefits

1. **Zero Configuration**: No need to register servers in `claude.json` - skills spawn on demand
2. **Session Persistence**: Maintain state across multiple operations (critical for browser automation, database queries)
3. **Type Safety**: Auto-generated tool schemas with parameter validation
4. **Discoverability**: Tools are documented in SKILL.md with trigger patterns
5. **Portability**: Skills are self-contained and can be shared across projects

---

## Quick Start

### Using the `/mcp-skill` Command

The fastest way to create a skill is via the `/mcp-skill` slash command:

```bash
/mcp-skill @modelcontextprotocol/server-postgres
```

This automatically:
1. Detects the MCP runtime (npx for npm packages, uvx for Python/git repos)
2. Spawns a temporary server to discover tools
3. Generates SKILL.md with categorized tool documentation
4. Creates session scripts with JSON-RPC communication
5. Provides usage examples

### Supported MCP Sources

| Source Type | Example | Runtime |
|-------------|---------|---------|
| npm package | `@modelcontextprotocol/server-postgres` | `npx -y {package}@latest` |
| Git repo | `git+https://github.com/user/mcp-server` | `uvx --from git+{url} {command}` |
| Local path | `~/projects/custom-mcp` | Auto-detected from `package.json` or `pyproject.toml` |

---

## Creating Skills

### Interactive Creation Flow

When you run `/mcp-skill {source}`, Claude will:

1. **Parse the MCP source**
   - npm package: Extract package name
   - Git URL: Extract command from repo name
   - Local path: Check for `package.json` or `pyproject.toml`

2. **Prompt for details**
   - Skill name (kebab-case, e.g., `database-inspector`)
   - Brief description for trigger patterns
   - Required environment variables (API keys, tokens)

3. **Discover tools**
   - Start temporary MCP server subprocess
   - Send JSON-RPC `initialize` and `tools/list` requests
   - Parse tool names, descriptions, and input schemas
   - Categorize by operation type (read, write, navigation, etc.)

4. **Generate files**
   - `SKILL.md`: Frontmatter, architecture diagram, tool docs
   - `{skill_name}_session.py`: Session manager with `start()`, `stop()`, `call_tool()`
   - `introspect_tools.py`: Standalone tool discovery script
   - `examples/workflows.md`: Common usage patterns

### Example: Creating a Postgres Skill

```bash
/mcp-skill @modelcontextprotocol/server-postgres
```

**Claude prompts:**
```
Skill name: postgres-inspector
Description: Query and inspect PostgreSQL databases
Environment variables: DATABASE_URL
```

**Generated structure:**
```
.claude/skills/postgres-inspector/
├── SKILL.md
├── scripts/
│   ├── postgres_inspector_session.py
│   └── introspect_tools.py
└── examples/
    └── workflows.md
```

**Usage:**
```bash
# Start persistent session
python ~/.claude/skills/postgres-inspector/scripts/postgres_inspector_session.py

# Or use directly from Claude Code
User: "Show me all tables in the database"
Claude: [Uses postgres-inspector skill → runs query → returns table list]
```

---

## Skill Architecture

### Subprocess Session Pattern (Standard)

Most MCP servers run as **subprocess sessions** spawned on-demand:

```
┌─────────────────┐     stdin/stdout      ┌─────────────────┐
│  Claude Code    │ ◄──── JSON-RPC ─────► │  MCP Server     │
│  (via script)   │                       │  (subprocess)   │
└─────────────────┘                       └─────────────────┘
```

**Key components:**

1. **Session Manager** (`{skill_name}_session.py`)
   - Spawns server subprocess with `stdin=PIPE`, `stdout=PIPE`
   - Sends JSON-RPC requests over stdin
   - Reads responses from stdout in background thread
   - Maintains message ID counter for request/response matching

2. **JSON-RPC Protocol** (MCP v2024-11-05)
   - `initialize`: Handshake with server capabilities
   - `tools/list`: Discover available tools
   - `tools/call`: Execute tool with arguments
   - `resources/list`: Get available resources (optional)

3. **Environment Loading**
   - Reads from `~/.env/services/.env`, `.env.local`, or current directory
   - Passes required env vars (API keys, connection strings) to subprocess

### HTTP Session Pattern (Remote Servers)

Some MCP servers are **hosted remotely** (e.g., Sentry, Render):

```
┌─────────────────┐     HTTPS/SSE         ┌─────────────────┐
│  Claude Code    │ ◄──── JSON-RPC ─────► │  Remote MCP     │
│  (via script)   │      + OAuth          │  (hosted)       │
└─────────────────┘                       └─────────────────┘
```

**Differences:**
- Uses HTTP POST with JSON-RPC body
- Supports OAuth authentication flows
- Session maintained via `Mcp-Session-Id` header
- May support SSE for streaming responses

---

## Session Management Patterns

### Pattern 1: Persistent Session (Recommended)

**Use when:** Tool calls need to maintain state (browser pages, database connections, conversation context)

**Implementation:**
```python
class SkillSession:
    def __init__(self):
        self.process = None
        self.msg_id = 1

    def start(self):
        self.process = subprocess.Popen(
            ['npx', '-y', 'mcp-server@latest'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        self._initialize()
        return self

    def _initialize(self):
        self._send_request('initialize', {
            'protocolVersion': '2024-11-05',
            'capabilities': {},
            'clientInfo': {'name': 'skill-session', 'version': '1.0'}
        })

    def call_tool(self, name, arguments):
        return self._send_request('tools/call', {
            'name': name,
            'arguments': arguments
        })

    def stop(self):
        if self.process:
            self.process.terminate()
```

**Example use case:** Browser automation
```python
session = ChromeSession()
session.start()

# Navigate to page
session.call_tool('navigate', {'url': 'https://example.com'})

# Click button (same browser instance)
session.call_tool('click', {'selector': '#submit'})

# Check console messages (same page context)
messages = session.call_tool('list_console_messages', {})

session.stop()
```

### Pattern 2: Single-Shot Execution

**Use when:** Each tool call is independent, no state needed

**Implementation:**
```python
def call_tool_once(tool_name, arguments):
    session = SkillSession()
    session.start()
    result = session.call_tool(tool_name, arguments)
    session.stop()
    return result
```

**Example use case:** Database queries
```python
# Each query is independent
result = call_tool_once('query', {
    'sql': 'SELECT * FROM users LIMIT 10'
})
```

### Pattern 3: HTTP Session (Remote Servers)

**Use when:** MCP server is hosted remotely (requires authentication)

**Implementation:**
```python
class RemoteSession:
    def __init__(self):
        self.msg_id = 1
        self.session_id = None
        self.token = os.environ.get('API_TOKEN')

    def _make_request(self, method, params=None):
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json',
        }
        if self.session_id:
            headers['Mcp-Session-Id'] = self.session_id

        body = {
            'jsonrpc': '2.0',
            'method': method,
            'params': params or {},
            'id': self.msg_id
        }
        self.msg_id += 1

        # Make HTTP request to remote MCP endpoint
        response = requests.post(
            'https://mcp.service.com/endpoint',
            headers=headers,
            json=body
        )
        return response.json()
```

---

## Best Practices

### 1. Environment Variable Management

**Recommended structure:**
```bash
# ~/.env/services/.env
POSTGRES_URL=postgresql://localhost/mydb
SENTRY_AUTH_TOKEN=sntryu_abc123...
RENDER_API_KEY=rnd_xyz789...
STRIPE_SECRET_KEY=sk_test_abc123...
```

**Load in session scripts:**
```python
def load_env_file():
    env_paths = [
        Path.home() / '.env' / 'services' / '.env',
        Path.cwd() / '.env',
    ]
    for env_file in env_paths:
        if env_file.exists():
            with open(env_file) as f:
                for line in f:
                    if line.strip() and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ.setdefault(key, value.strip())
```

### 2. Error Handling

**Robust error handling in session managers:**
```python
def call_tool(self, name, arguments):
    try:
        response = self._send_request('tools/call', {
            'name': name,
            'arguments': arguments
        })

        if 'error' in response:
            raise RuntimeError(f"Tool error: {response['error']}")

        return response.get('result', {})

    except subprocess.TimeoutExpired:
        raise TimeoutError(f"Tool '{name}' timed out after 30s")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON response: {e}")
```

### 3. Tool Categorization

**Organize tools by operation type in SKILL.md:**

```markdown
## Available Tools

### Read Operations (5 tools)
- **get_user** - Fetch user by ID
- **list_orders** - List all orders
- **search_products** - Search product catalog

### Write Operations (3 tools)
- **create_user** - Create new user
- **update_order** - Modify order status

### Destructive Operations (2 tools)
- **delete_user** - Permanently remove user
- **purge_cache** - Clear all cached data
```

### 4. Usage Documentation

**Include concrete examples in workflows.md:**

```markdown
## Example: Database Schema Inspection

**Goal:** Understand table relationships in a new database

**Steps:**
1. List all tables
   ```bash
   python session.py --tool query --args '{"sql": "SELECT table_name FROM information_schema.tables"}'
   ```

2. Get column info for key tables
   ```bash
   python session.py --tool query --args '{"sql": "SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '\''users'\''"}'
   ```

3. Find foreign key relationships
   ```bash
   python session.py --tool query --args '{"sql": "SELECT * FROM information_schema.table_constraints WHERE constraint_type = '\''FOREIGN KEY'\''"}'
   ```

**Result:** Complete understanding of database schema and relationships
```

### 5. Read-Only Tool Allowlists

**For production safety, restrict destructive operations:**

```python
# In session script
READONLY_TOOLS = {
    'list_services',
    'get_logs',
    'query_database',  # SELECT only
    'get_metrics',
}

def call_tool(self, name, arguments):
    if name not in READONLY_TOOLS:
        raise PermissionError(
            f"Tool '{name}' is disabled for safety. "
            f"Allowed: {', '.join(READONLY_TOOLS)}"
        )
    return self._send_request('tools/call', {'name': name, 'arguments': arguments})
```

---

## Examples

### Example 1: Error Tracking Skill

**Skill:** Sentry integration for production error investigation

**Created with:**
```bash
/mcp-skill https://mcp.sentry.dev
```

**Common workflows:**
```python
# Search for errors in a specific file
session.call_tool('search_issues', {
    'query': 'error in checkout.py'
})

# Get detailed issue with stack trace
session.call_tool('get_issue', {
    'issue_id': '12345'
})

# Trigger AI root cause analysis
session.call_tool('trigger_seer_analysis', {
    'issue_id': '12345'
})

# Get AI-generated fix suggestions
session.call_tool('get_seer_recommendations', {
    'issue_id': '12345'
})
```

**Value:** Eliminate browser context switching - Claude investigates errors directly

### Example 2: Database Query Skill

**Skill:** PostgreSQL read-only query interface

**Created with:**
```bash
/mcp-skill @modelcontextprotocol/server-postgres
```

**Common workflows:**
```python
# Explore database structure
session.call_tool('query', {
    'sql': 'SELECT table_name FROM information_schema.tables WHERE table_schema = \'public\''
})

# Analyze data
session.call_tool('query', {
    'sql': 'SELECT status, COUNT(*) FROM orders GROUP BY status'
})

# Debug ORM queries
session.call_tool('query', {
    'sql': 'EXPLAIN ANALYZE SELECT * FROM users WHERE email LIKE \'%@example.com\''
})
```

**Value:** Direct database access for schema inspection, data analysis, query debugging

### Example 3: Browser Automation Skill

**Skill:** Chrome DevTools for UI testing and debugging

**Created with:**
```bash
/mcp-skill chrome-devtools-mcp
```

**Common workflows:**
```python
# Navigate to page
session.call_tool('navigate_page', {
    'url': 'https://app.example.com/dashboard'
})

# Check for JavaScript errors
messages = session.call_tool('list_console_messages', {})
errors = [m for m in messages if m['level'] == 'error']

# Take screenshot
session.call_tool('take_screenshot', {
    'fullPage': True
})

# Monitor network requests
requests = session.call_tool('list_network_requests', {})
failed = [r for r in requests if r['status'] >= 400]
```

**Value:** Automated browser testing, visual regression detection, console error monitoring

### Example 4: Multi-AI Consensus Skill

**Skill:** Orchestrate multiple AI models for code review and decision-making

**Created with:**
```bash
/mcp-skill zen-mcp-server
```

**Common workflows:**
```python
# Get consensus from multiple models
session.call_tool('consensus', {
    'prompt': 'Should we use REST or GraphQL for this API?'
})

# Comprehensive code review
session.call_tool('codereview', {
    'files': ['src/auth/login.ts'],
    'severity': 'critical'
})

# Security audit with OWASP analysis
session.call_tool('secaudit', {
    'path': 'src/payment/checkout.ts'
})

# Challenge Claude's own reasoning
session.call_tool('challenge', {
    'claim': 'We should use microservices for this feature'
})
```

**Value:** Multi-perspective analysis, reduced blind spots, more robust decisions

### Example 5: Infrastructure Management Skill

**Skill:** Render.com deployment and log monitoring

**Created with:**
```bash
/mcp-skill https://mcp.render.com
```

**Common workflows:**
```python
# List services in workspace
session.call_tool('list_services', {})

# Get deployment logs
session.call_tool('list_logs', {
    'service_id': 'srv-xyz',
    'limit': 100
})

# Check service health
session.call_tool('get_service', {
    'service_id': 'srv-xyz'
})

# Query production database (read-only)
session.call_tool('query_render_postgres', {
    'instance_id': 'dpg-abc',
    'sql': 'SELECT COUNT(*) FROM users'
})
```

**Value:** Production debugging without leaving Claude Code, log analysis, health monitoring

---

## Troubleshooting

### Issue: Server Fails to Start

**Symptoms:**
```
Error: Command not found: npx
Error: spawn ENOENT
```

**Solutions:**
1. Verify runtime is installed:
   ```bash
   npx --version   # For npm packages
   uvx --version   # For Python/git packages
   ```

2. Check MCP package name:
   ```bash
   npx -y @modelcontextprotocol/server-postgres@latest --help
   ```

3. Review stderr output for dependency errors

### Issue: Tools Not Discovered

**Symptoms:**
```
No tools found from server
tools/list returned empty array
```

**Solutions:**
1. Manually test server:
   ```bash
   npx -y {package}@latest
   # Send: {"jsonrpc":"2.0","method":"tools/list","id":1}
   ```

2. Check server supports `tools/list` (some servers only expose resources)

3. Verify protocol version compatibility (use `2024-11-05`)

### Issue: Environment Variables Not Loaded

**Symptoms:**
```
ERROR: DATABASE_URL environment variable not set
Authentication failed: missing API key
```

**Solutions:**
1. Check env file exists and has correct format:
   ```bash
   cat ~/.env/services/.env
   # Should be: KEY=value (no spaces around =)
   ```

2. Verify load_env_file() is called before session.start()

3. Export manually for testing:
   ```bash
   export DATABASE_URL="postgresql://localhost/mydb"
   python session.py
   ```

### Issue: Session State Lost

**Symptoms:**
```
Console messages: []  (expected errors)
Network requests: []  (expected requests)
Page not found after navigation
```

**Solutions:**
1. Use persistent session pattern (don't spawn new process per call)

2. For browser automation, use Node.js session template:
   ```bash
   node ~/.claude/skills/{skill}/scripts/persistent-session.mjs
   ```

3. Verify `start()` is called once, not per tool call

### Issue: Permission Denied

**Symptoms:**
```
EACCES: permission denied
bash: npx: command not found
```

**Solutions:**
1. Make session script executable:
   ```bash
   chmod +x ~/.claude/skills/{skill}/scripts/{skill}_session.py
   ```

2. Install Node.js/npm globally:
   ```bash
   # macOS
   brew install node

   # Linux
   curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
   sudo apt-get install -y nodejs
   ```

3. Add npm global bin to PATH:
   ```bash
   export PATH="$HOME/.npm-global/bin:$PATH"
   ```

---

## Advanced Topics

### Custom Tool Filtering

Filter tools based on patterns or capabilities:

```python
class FilteredSession(BaseSession):
    ALLOWED_PATTERNS = [
        r'^get_.*',      # All read operations
        r'^list_.*',     # All list operations
        r'.*_readonly$', # Explicitly readonly tools
    ]

    def call_tool(self, name, arguments):
        import re
        if not any(re.match(p, name) for p in self.ALLOWED_PATTERNS):
            raise PermissionError(f"Tool '{name}' not in allowlist")
        return super().call_tool(name, arguments)
```

### Tool Result Caching

Cache expensive tool calls (schema queries, API metadata):

```python
class CachedSession(BaseSession):
    def __init__(self):
        super().__init__()
        self.cache = {}
        self.cacheable_tools = {'list_tables', 'get_schema'}

    def call_tool(self, name, arguments):
        cache_key = f"{name}:{json.dumps(arguments, sort_keys=True)}"

        if name in self.cacheable_tools and cache_key in self.cache:
            return self.cache[cache_key]

        result = super().call_tool(name, arguments)

        if name in self.cacheable_tools:
            self.cache[cache_key] = result

        return result
```

### Multi-Tool Orchestration

Chain multiple tool calls for complex workflows:

```python
def investigate_production_error(error_message):
    sentry = SentrySession().start()
    db = PostgresSession().start()
    logs = RenderSession().start()

    try:
        # 1. Find related issues in Sentry
        issues = sentry.call_tool('search_issues', {
            'query': error_message
        })

        # 2. Query database for affected users
        affected = db.call_tool('query', {
            'sql': f"SELECT user_id FROM error_logs WHERE message LIKE '%{error_message}%'"
        })

        # 3. Get production logs
        recent_logs = logs.call_tool('list_logs', {
            'service_id': 'srv-prod',
            'limit': 500
        })

        return {
            'issues': issues,
            'affected_users': affected,
            'logs': recent_logs
        }

    finally:
        sentry.stop()
        db.stop()
        logs.stop()
```

---

## Resources

### MCP Specification
- [Model Context Protocol Docs](https://modelcontextprotocol.io/)
- [JSON-RPC 2.0 Specification](https://www.jsonrpc.org/specification)

### Official MCP Servers
- [@modelcontextprotocol/server-postgres](https://github.com/modelcontextprotocol/servers/tree/main/src/postgres)
- [@modelcontextprotocol/server-filesystem](https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem)
- [@modelcontextprotocol/server-github](https://github.com/modelcontextprotocol/servers/tree/main/src/github)
- [Sentry MCP](https://docs.sentry.io/product/sentry-mcp/)
- [Render MCP](https://docs.render.com/mcp)

### Community MCP Servers
- [Awesome MCP Servers](https://github.com/punkpeye/awesome-mcp-servers)

---

## Contributing

### Sharing Skills

To share a skill with the community:

1. **Test thoroughly** with various inputs and edge cases
2. **Document trigger patterns** in SKILL.md frontmatter
3. **Provide examples** in workflows.md
4. **Add error handling** for common failure modes
5. **Remove project-specific paths** and credentials

### Skill Template Repository

Consider creating a template repository with:
- Standardized session manager base class
- Environment loading utilities
- Error handling patterns
- Testing framework for tool calls

---

## License

This MCP skills framework pattern is provided as-is for use in any project. Individual MCP servers may have their own licenses - check server documentation before use.
