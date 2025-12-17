# MCP Skills

On-demand MCP server integrations that stay out of your context until you need them.

## Why Skills?

MCP servers registered in `claude.json` are **always loaded**, adding tool definitions to every conversation. Skills solve this by:

1. **Staying dormant** until explicitly invoked
2. **Providing context** only when relevant
3. **Cleaning up** when the session ends

## Available Skills

| Skill | Description | Triggers |
|-------|-------------|----------|
| [chrome-devtools](./chrome-devtools/) | Browser automation and testing | "test the page", "take screenshot", "console errors" |
| [postgres](./postgres/) | Query PostgreSQL databases | "query database", "table structure", "run SQL" |
| [sentry](./sentry/) | Error tracking investigation | "production error", "check errors", "stack trace" |
| [github](./github/) | Repository and issue management | "github issue", "pull request", "create PR" |

## Quick Start

### Using a Skill Directly

```python
# Chrome DevTools
from chrome_devtools.scripts.chrome_devtools_session import ChromeDevToolsSession

with ChromeDevToolsSession() as browser:
    browser.navigate("https://example.com")
    browser.screenshot(full_page=True)
    errors = browser.get_console_logs()

# PostgreSQL
from postgres.scripts.postgres_session import PostgresSession

with PostgresSession() as db:
    tables = db.list_tables()
    users = db.query("SELECT * FROM users LIMIT 10")

# Sentry
from sentry.scripts.sentry_session import SentrySession

with SentrySession() as sentry:
    issues = sentry.search_issues("is:unresolved level:error")

# GitHub
from github.scripts.github_session import GitHubSession

with GitHubSession() as gh:
    issues = gh.list_issues("owner", "repo")
```

### CLI Usage

Each skill has a CLI interface:

```bash
# Chrome DevTools
python .claude/skills/chrome-devtools/scripts/chrome_devtools_session.py --interactive

# PostgreSQL
python .claude/skills/postgres/scripts/postgres_session.py --tables
python .claude/skills/postgres/scripts/postgres_session.py --sql "SELECT COUNT(*) FROM users"

# Sentry
python .claude/skills/sentry/scripts/sentry_session.py --search "is:unresolved"

# GitHub
python .claude/skills/github/scripts/github_session.py --issues owner/repo
```

## Creating New Skills

### Using the Generator

```bash
/mcp-skill @modelcontextprotocol/server-postgres
```

This will:
1. Prompt for skill name, description, and required env vars
2. Introspect the MCP server to discover tools
3. Generate SKILL.md, session script, and examples

### Manual Creation

Create a directory under `.claude/skills/` with:

```
.claude/skills/my-skill/
├── SKILL.md                    # Skill definition (required)
├── scripts/
│   └── my_skill_session.py     # Session manager (required)
└── examples/
    └── workflows.md            # Usage examples (optional)
```

The session script should extend `MCPSession` from `_base/scripts/mcp_session.py`.

## Environment Variables

Skills load environment variables from (in order):

1. `~/.env/services/.env` - Recommended for API tokens
2. `~/.env/.env`
3. `.env.local` - Project-specific
4. `.env`

Example `~/.env/services/.env`:
```bash
DATABASE_URL=postgresql://user@localhost:5432/mydb
SENTRY_AUTH_TOKEN=sntryu_xxxxx
GITHUB_PERSONAL_ACCESS_TOKEN=ghp_xxxxx
```

## Architecture

```
┌─────────────────┐     stdin/stdout      ┌─────────────────┐
│  Claude Code    │ ◄──── JSON-RPC ─────► │  MCP Server     │
│  (skill script) │                       │  (subprocess)   │
└─────────────────┘                       └─────────────────┘
```

Skills use the MCP protocol (JSON-RPC 2.0 over stdin/stdout) to communicate with MCP servers running as subprocesses.

### Special Cases

**Chrome DevTools**: Manages both Chrome browser and MCP server lifecycle. The skill launches Chrome with remote debugging before starting the MCP server.

**Sentry**: Uses HTTP-based MCP (hosted at `https://mcp.sentry.dev`) instead of subprocess.

## File Structure

```
.claude/skills/
├── _base/                      # Shared infrastructure
│   └── scripts/
│       ├── mcp_session.py      # Base session class
│       └── skill_generator.py  # Skill generator
├── chrome-devtools/            # Browser automation
├── postgres/                   # Database queries
├── sentry/                     # Error tracking
├── github/                     # Repository management
└── README.md                   # This file
```

## Troubleshooting

### Skill Won't Start

1. Check required environment variables are set
2. Verify the MCP server package exists: `npx -y @package/name --help`
3. Check for port conflicts (Chrome uses 9222)

### No Tools Discovered

1. Server may not support `tools/list` - check MCP server docs
2. Protocol version mismatch - skills use `2024-11-05`

### Session State Lost

1. Use the context manager pattern (`with Session() as s:`)
2. Don't create new sessions for each tool call
3. For Chrome, ensure Chrome process stays alive
