# Migration from pip-tools to uv

This document details the steps taken to migrate this project from pip-tools to uv for dependency management.

## Why uv?

[uv](https://github.com/astral-sh/uv) is a new package installer and resolver for Python that offers several advantages:

- Much faster installation times (10-100x faster than pip)
- Reliable dependency resolution
- Consistent lockfiles
- Built-in virtual environment management
- Compatible with pip/pip-tools workflows

## Migration Steps Completed

1. Created a new `requirements/uv` directory
2. Created simplified requirements files:
   - `base.txt` - Essential packages only
   - `dev.txt` - Development dependencies
   - `prod.txt` - Production dependencies
3. Generated lockfiles with pinned versions:
   - `base.lock.txt`
   - `dev.lock.txt`
   - `prod.lock.txt`
4. Created helper scripts:
   - `install.sh` - For installing dependencies
   - `test.sh` - For testing the setup
   - `generate_deployment_requirements.sh` - For creating requirements.txt
5. Updated documentation in:
   - `README.md`
   - `CLAUDE.md`
   - `requirements/README.md`
6. Updated build.sh script to use uv for deployments
7. Moved old pip-tools files to requirements/legacy directory
8. Generated requirements.txt for deployment platforms

## Removed Dependencies

These dependencies were removed during migration:
- Redis and redisgraph (no longer needed)
- Other unused integrations

## Using the New System

See `requirements/README.md` for detailed usage instructions.

Basic usage:
```bash
# Install uv
pip install uv

# Install dependencies
./requirements/uv/install.sh dev  # For development
./requirements/uv/install.sh prod  # For production
```

## For Deployments

A requirements.txt file is automatically generated for deployment platforms:

```bash
./requirements/uv/generate_deployment_requirements.sh
```

This creates a requirements.txt file in the project root that can be used by platforms like Render or Heroku.

## Verifying the Setup

Run the test script to verify the uv setup:
```bash
./requirements/uv/test.sh
```