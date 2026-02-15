# /mcp-skill - Generate MCP Skills

Generate a Claude Code skill from any MCP server source.

## What This Command Does

When invoked with an MCP source, this command:

1. **Parses the source** - Determines runtime (npx, uvx, local) from the input
2. **Prompts for details** - Asks for skill name, description, and required env vars
3. **Introspects the server** - Spawns a temp server to discover all available tools
4. **Generates the skill** - Creates SKILL.md, session scripts, and examples

## Usage

```
/mcp-skill <source>
```

### Source Types

| Type | Example | Runtime |
|------|---------|---------|
| npm package | `@modelcontextprotocol/server-postgres` | npx |
| npm scoped | `@anthropic/mcp-server-chrome` | npx |
| Git URL | `git+https://github.com/user/mcp-server` | uvx |
| GitHub shorthand | `https://github.com/user/mcp-server` | uvx |
| Local path | `~/projects/my-mcp-server` | auto-detect |

## Examples

### PostgreSQL Skill
```
/mcp-skill @modelcontextprotocol/server-postgres
```

When prompted:
- **Name**: postgres
- **Description**: Query PostgreSQL databases
- **Required env**: DATABASE_URL

### Sentry Skill (Remote)
```
/mcp-skill https://mcp.sentry.dev
```

When prompted:
- **Name**: sentry
- **Description**: Sentry error tracking and investigation
- **Required env**: SENTRY_AUTH_TOKEN

### Custom MCP Server
```
/mcp-skill ~/projects/my-custom-mcp
```

## Generated Structure

```
.claude/skills/{skill-name}/
├── SKILL.md                    # Tool docs and trigger patterns
├── scripts/
│   ├── {skill}_session.py      # Session manager
│   └── tool_schemas.json       # Full tool definitions
└── examples/
    └── workflows.md            # Usage examples
```

## After Generation

The skill is immediately available. Claude Code will:
1. Detect trigger patterns from SKILL.md frontmatter
2. Invoke the skill session when relevant context appears
3. Clean up session resources when done

## Manual Testing

```bash
# List discovered tools
python .claude/skills/{skill}/scripts/{skill}_session.py --list-tools

# Interactive session
python .claude/skills/{skill}/scripts/{skill}_session.py --interactive

# Single tool call
python .claude/skills/{skill}/scripts/{skill}_session.py \
  --tool query \
  --args '{"sql": "SELECT 1"}'
```

---

## Instructions for Claude

When the user invokes `/mcp-skill <source>`, follow these steps:

### Step 1: Parse the Source

Identify the MCP source type:
- **npm package**: Starts with `@` or is a simple name without `/`
- **Git URL**: Contains `github.com` or starts with `git+`
- **HTTP URL**: Starts with `http://` or `https://` (remote MCP server)
- **Local path**: Starts with `/`, `~`, or `.`

### Step 2: Gather Information

Ask the user for:
1. **Skill name** (kebab-case, e.g., `postgres`, `sentry`, `chrome-devtools`)
2. **Brief description** (one line, for trigger patterns)
3. **Required environment variables** (if any - API keys, connection strings)

### Step 3: Generate the Skill

Use the skill generator script:

```bash
python .claude/skills/_base/scripts/skill_generator.py \
  --source "<source>" \
  --name "<name>" \
  --description "<description>" \
  --env VAR1 --env VAR2  # if any required env vars
```

If the generator fails (e.g., server won't start), help troubleshoot:
- Check if the MCP package exists
- Verify required env vars are set
- Try running the MCP command manually to see errors

### Step 4: Verify and Report

After generation:
1. List the created files
2. Show the number of tools discovered
3. Provide example usage

### Special Cases

**Chrome DevTools**: Already has a custom skill at `.claude/skills/chrome-devtools/` that handles Chrome lifecycle. Don't regenerate unless asked.

**HTTP/Remote MCPs**: These require OAuth or API tokens. The generator will handle subprocess MCPs but HTTP MCPs need manual configuration.

**Failed Introspection**: If the MCP server fails to start, check:
- Package name spelling
- Required runtime (Node.js for npx, Python for uvx)
- Environment variables that must be set first
