# Claude Code Skills

Custom skills that extend Claude Code's capabilities for this Django project.

## What Are Skills?

Skills are markdown files (`SKILL.md`) that provide Claude Code with specialized knowledge and workflows for specific tasks. They stay dormant until relevant, keeping conversations focused.

## Available Skills

| Skill | Description |
|-------|-------------|
| [prime](../commands/prime.md) | Application primer with full architecture context |

## Example Skills

The `examples/` directory contains example skill templates you can adapt:

- **django-admin** - Common Django admin and management commands
- **deployment** - Deployment checklist and procedures

## Creating New Skills

Create a directory under `.claude/skills/` with a `SKILL.md` file:

```
.claude/skills/my-skill/
└── SKILL.md    # Skill definition with triggers and instructions
```

### SKILL.md Structure

```markdown
---
name: my-skill
description: What this skill does
triggers:
  - "keyword or phrase that activates this skill"
  - "another trigger phrase"
---

# My Skill

## Context
Background information Claude needs.

## Workflows
Step-by-step instructions for common tasks.

## Commands
Specific commands or code patterns to use.
```

### Tips

- Keep skills focused on one domain
- Include concrete commands, not just concepts
- Add trigger phrases that match how you naturally ask for help
- Reference project-specific paths and conventions
