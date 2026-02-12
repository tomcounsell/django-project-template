#!/bin/bash

# Quick setup script for new developers
# This script sets up the development environment using uv

set -e  # Exit on error

echo "🚀 Django Project Template - Development Setup"
echo "=============================================="
echo ""

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "📦 uv is not installed. Installing uv..."
    pip install uv
    echo "✅ uv installed successfully"
else
    echo "✅ uv is already installed"
fi

# Check Python version
python_version=$(python3 --version | cut -d " " -f 2 | cut -d "." -f 1-2)
required_version="3.11"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Error: Python $required_version or higher is required (found $python_version)"
    exit 1
fi
echo "✅ Python version check passed ($python_version)"

# Sync dependencies based on environment
if [ "$1" == "prod" ]; then
    echo ""
    echo "📦 Installing production dependencies..."
    uv sync
elif [ "$1" == "test" ]; then
    echo ""
    echo "📦 Installing test dependencies..."
    uv sync --extra test
else
    echo ""
    echo "📦 Installing all development dependencies..."
    uv sync --all-extras
fi

echo ""
echo "✅ Dependencies installed successfully!"

# Zed editor setup
echo ""
read -p "Would you like to set up Zed editor configuration? (y/N) " setup_zed
if [[ "$setup_zed" =~ ^[Yy]$ ]]; then
    mkdir -p .zed
    cat > .zed/tasks.json << 'TASKS'
[
  {
    "label": "Django Server",
    "command": "uv run python manage.py runserver",
    "env": { "DJANGO_SETTINGS_MODULE": "settings", "PYTHONUNBUFFERED": "1" },
    "use_new_terminal": true,
    "allow_concurrent_runs": false
  },
  {
    "label": "Tailwind Watch",
    "command": "uv run python manage.py tailwind watch",
    "env": { "DJANGO_SETTINGS_MODULE": "settings", "PYTHONUNBUFFERED": "1" },
    "use_new_terminal": true,
    "allow_concurrent_runs": false
  },
  {
    "label": "Run Tests",
    "command": "DJANGO_SETTINGS_MODULE=settings uv run pytest -v",
    "use_new_terminal": false
  },
  {
    "label": "Run Tests (current file)",
    "command": "DJANGO_SETTINGS_MODULE=settings uv run pytest -v $ZED_FILE",
    "use_new_terminal": false
  },
  {
    "label": "Django Shell",
    "command": "uv run python manage.py shell",
    "env": { "DJANGO_SETTINGS_MODULE": "settings", "PYTHONUNBUFFERED": "1" },
    "use_new_terminal": true
  },
  {
    "label": "Dev (Server + Tailwind)",
    "command": "uv run python manage.py runserver & uv run python manage.py tailwind watch; wait",
    "env": { "DJANGO_SETTINGS_MODULE": "settings", "PYTHONUNBUFFERED": "1" },
    "use_new_terminal": true
  }
]
TASKS
    cat > .zed/settings.json << 'SETTINGS'
{
  "languages": {
    "Python": {
      "language_servers": ["pyright", "ruff"]
    }
  }
}
SETTINGS
    echo "✅ Zed config created in .zed/ (tasks + settings)"
    echo "   See docs/ZED_SETUP.md for keybindings and more details"
fi

echo ""
echo "Next steps:"
echo "  1. Copy .env.example to .env.local and configure"
echo "  2. Set up your database"
echo "  3. Run migrations: uv run python manage.py migrate"
echo "  4. Start development server: uv run python manage.py runserver"
echo ""
echo "Happy coding! 🎉"
