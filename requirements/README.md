# Dependency Management with uv

This project uses [uv](https://github.com/astral-sh/uv) for dependency management. uv is a fast, modern Python package installer and resolver that replaces pip-tools with significant performance improvements.

## Files

- `base.txt` - Core dependencies for all environments
- `dev.txt` - Additional dependencies for development
- `prod.txt` - Production dependencies
- `base.lock.txt` - Locked dependencies for base
- `dev.lock.txt` - Locked dependencies for development
- `prod.lock.txt` - Locked dependencies for production
- `install.sh` - Helper script to install dependencies
- `generate_deployment_requirements.sh` - Script to create requirements.txt
- `test.sh` - Test script for validating setup

## Installation

```bash
# Install uv
pip install uv

# Install development dependencies
./requirements/install.sh dev

# For production
./requirements/install.sh prod
```

## Updating Dependencies

To update lockfiles after changing requirements:

```bash
# Update base lockfile
uv pip compile requirements/base.txt -o requirements/base.lock.txt

# Update development lockfile
uv pip compile requirements/dev.txt -o requirements/dev.lock.txt

# Update production lockfile
uv pip compile requirements/prod.txt -o requirements/prod.lock.txt
```

## For Deployments

Generate a requirements.txt file for deployment platforms:

```bash
./requirements/generate_deployment_requirements.sh
```

This creates a `requirements.txt` file in the project root that can be used by deployment platforms like Render or Heroku.

## Using Virtual Environments with uv

```bash
# Create a virtual environment in the current directory
uv venv

# Activate it
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
./requirements/install.sh dev
```