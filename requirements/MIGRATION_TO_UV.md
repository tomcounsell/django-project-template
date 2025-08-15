# Migration to Modern uv Workflow

## Summary of Changes

This project has been migrated from a pip-tools based workflow to uv's modern pyproject.toml-based approach.

### What Changed

#### Before (Old System)
```
requirements/
├── base.txt          # Base dependencies
├── dev.txt           # Development dependencies  
├── prod.txt          # Production dependencies
├── base.lock.txt     # Locked versions
├── dev.lock.txt      # Locked versions
├── prod.lock.txt     # Locked versions
├── install.sh        # Installation script
└── test.sh          # Test script
```

#### After (New System)
```
/
├── pyproject.toml    # Single source of truth for all dependencies
├── uv.lock          # Single lock file for reproducible installs
requirements/
├── README.md        # Documentation
├── setup.sh         # Simple setup script
└── legacy/          # Archived old files for reference
```

## For Developers

### Installing Dependencies

**Old way:**
```bash
./requirements/install.sh dev
```

**New way:**
```bash
uv sync --all-extras    # Install everything for development
# or
./requirements/setup.sh  # Convenience wrapper
```

### Adding New Dependencies

**Old way:**
1. Edit requirements/base.txt or dev.txt
2. Run `uv pip compile requirements/dev.txt -o requirements/dev.lock.txt`
3. Commit both files

**New way:**
```bash
uv add package-name        # For production
uv add --dev package-name  # For development
# Automatically updates pyproject.toml and uv.lock
```

### Updating Dependencies

**Old way:**
```bash
uv pip compile --upgrade requirements/dev.txt -o requirements/dev.lock.txt
```

**New way:**
```bash
uv lock --upgrade                           # Update all
uv add package --upgrade-package package    # Update specific
```

## For CI/CD

### GitHub Actions
Update your workflows to use:
```yaml
- name: Install uv
  uses: astral-sh/setup-uv@v3
  
- name: Install dependencies
  run: uv sync --frozen
```

### Docker
Update Dockerfile:
```dockerfile
# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-dev
```

### Deployment Platforms

Most modern platforms (Render, Railway, Fly.io) support pyproject.toml directly.

For legacy platforms requiring requirements.txt:
```bash
uv export --no-dev > requirements.txt
```

## Benefits of the New System

1. **Single Source of Truth**: All dependencies in pyproject.toml
2. **Faster**: uv is 10-100x faster than pip
3. **Reproducible**: uv.lock ensures everyone gets exact same versions
4. **Simpler**: No need to maintain multiple .txt and .lock.txt files
5. **Modern**: Follows Python packaging best practices
6. **Better Resolution**: More reliable dependency conflict resolution

## FAQ

**Q: Where are the old requirements files?**
A: Archived in `requirements/legacy/` for reference.

**Q: Do I need to activate a virtual environment?**
A: No, uv handles this automatically with `uv run` commands.

**Q: How do I see what's installed?**
A: Run `uv pip list` or check `uv.lock`.

**Q: Can I still use pip?**
A: You can, but it's not recommended. Use uv for consistency.

**Q: What about production deployments?**
A: Use `uv sync --frozen --no-dev` or export to requirements.txt if needed.

## Rollback Plan

If you need to rollback:
1. Restore files from `requirements/legacy/`
2. Delete `uv.lock`
3. Revert changes to `pyproject.toml`

However, the new system is fully backward compatible and more maintainable.