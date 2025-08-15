# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Core Commands

### Development Setup
```bash
# Initial setup (only needed once)
python3 -m venv venv && source venv/bin/activate && pip install uv
uv sync --all-extras  # Install all dependencies
cp .env.example .env.local
# Edit .env.local with: DATABASE_URL=postgres://$(whoami)@localhost:5432/django-project-template
createdb django-project-template
uv run python manage.py migrate
uv run python manage.py createsuperuser

# Alternative: Use the setup script
./requirements/setup.sh  # Installs all dev dependencies
```

### Daily Development
```bash
# Start development server
uv run python manage.py runserver

# Run Django shell
uv run python manage.py shell

# Make and apply migrations
uv run python manage.py makemigrations
uv run python manage.py migrate

# Collect static files
uv run python manage.py collectstatic --noinput
```

### Testing
```bash
# Run all tests
DJANGO_SETTINGS_MODULE=settings pytest

# Run specific test file
DJANGO_SETTINGS_MODULE=settings pytest apps/common/tests/test_models/test_address.py -v

# Run specific test class
DJANGO_SETTINGS_MODULE=settings pytest apps/common/tests/test_models/test_address.py::AddressModelTestCase -v

# Run specific test method
DJANGO_SETTINGS_MODULE=settings pytest apps/common/tests/test_models/test_address.py::AddressModelTestCase::test_string_representation -v

# Run tests by keyword
DJANGO_SETTINGS_MODULE=settings pytest -k "user and not stripe" -v

# Run with coverage
DJANGO_SETTINGS_MODULE=settings pytest --cov=apps --cov-report=html:apps/common/tests/coverage_html_report

# Run E2E tests
python tools/testing/browser_test_runner.py apps/**/tests/test_e2e_*.py

# Run visual tests  
python tools/testing/browser_test_runner.py apps/**/tests/test_visual_*.py
```

### Code Quality
```bash
# Format code (use before committing)
black . && isort .

# Run linting
flake8 . && mypy .

# Alternative: Use Ruff
uv run ruff format .
uv run ruff check . --fix

# Type checking
uv run pyright
```

### Package Management (MUST use uv)
```bash
# Add production dependency
uv add package-name

# Add dev dependency
uv add --dev package-name

# Add to optional group (test, e2e)
uv add --optional test package-name

# Upgrade specific package
uv add package-name --upgrade-package package-name

# Sync dependencies
uv sync --all-extras     # Install everything
uv sync                  # Production only
uv sync --extra dev      # Production + dev

# NEVER use: pip install, uv pip install, or @latest syntax
```

## Architecture Overview

### Project Structure
```
django-project-template/
├── apps/                    # Django applications
│   ├── common/             # Core models, behaviors, utilities
│   ├── public/             # Web UI, templates, HTMX views  
│   ├── api/                # REST API endpoints
│   ├── integration/        # Third-party service integrations
│   └── ai/                 # AI model integrations
├── settings/               # Modular Django settings
│   ├── __init__.py        # Settings orchestrator
│   ├── env.py             # Environment detection
│   ├── base.py            # Core Django settings
│   ├── database.py        # Database configuration
│   ├── third_party.py     # External service settings
│   ├── local.py           # Local development overrides
│   └── production.py      # Production settings
├── templates/              # All HTML templates (no app-specific)
├── static/                 # All static files (no app-specific)
└── staticfiles/           # Collected static files (gitignored)
```

### Settings Architecture
Settings are loaded in a specific order via `settings/__init__.py`:
1. **env.py** - Environment detection (LOCAL, STAGE, PRODUCTION)
2. **base.py** - Core Django configuration
3. **database.py** - Database setup using DATABASE_URL
4. **third_party.py** - External service configurations
5. **production.py** - Production-specific settings (if PRODUCTION)
6. **local.py** - Local development overrides (if LOCAL)

Environment is determined by `DEPLOYMENT_TYPE` in `.env.local` file.

### App Dependencies
- **common**: Foundation app with User model, behavior mixins, utilities
- **public**: Depends on common, provides web UI with HTMX
- **api**: Depends on common, provides REST endpoints
- **integration**: Depends on common, handles external services
- **ai**: Depends on common, handles AI integrations

### Behavior Mixins (apps/common/behaviors/)
Reusable model mixins that add common functionality:
- **Timestampable**: `created_at`, `modified_at` fields
- **Authorable**: Track content authors
- **Publishable**: Publishing workflow management
- **Expirable**: Content expiration handling
- **Permalinkable**: URL slug generation
- **Locatable**: Location/address fields
- **Annotatable**: Notes relationship

## Critical Development Guidelines

### Package Management
- **ONLY use uv** for all package operations
- Dependencies defined in `pyproject.toml`
- Python version requirement: >=3.11
- NEVER use pip directly or `uv pip install`

### Templates and Frontend
- All templates in `/templates` directory (NOT in apps)
- Use template inheritance with base templates
- HTMX preferred over JavaScript for interactivity
- Tailwind CSS v4 with django-tailwind-cli
- View classes: `MainContentView` for pages, `HTMXView` for HTMX components

### Testing Requirements
- Write tests BEFORE implementing features (TDD)
- Never use SQLite for tests (app uses Postgres JSON fields)
- Tests organized by type in `apps/{app_name}/tests/`
- Factory classes in `apps/common/tests/factories.py`
- 100% coverage goal for models and behaviors

### Code Style
- Black formatter (line length 88)
- Type hints required for all code
- Datetime fields must end with `_at`
- Follow PEP 8 with Black formatting
- Group imports: stdlib, third-party, Django, local

### Database
- PostgreSQL required (JSON field support)
- Migrations: Don't run without approval
- Use behavior mixins for common model patterns
- Connection configured via DATABASE_URL

### Environment Configuration
- Local settings in `.env.local` (not committed)
- Copy from `.env.example` for initial setup
- Key variables:
  - `DATABASE_URL`: PostgreSQL connection string
  - `DEPLOYMENT_TYPE`: LOCAL/STAGE/PRODUCTION
  - `SECRET_KEY`: Django secret key
  - `DEBUG`: True for local development

## Common Development Tasks

### Adding a New Model
1. Create model in appropriate app's `models/` directory
2. Use behavior mixins from `apps/common/behaviors/`
3. Write tests first in `tests/test_models/`
4. Create and apply migrations
5. Register in admin if needed

### Creating HTMX Views
1. Inherit from `HTMXView` in `apps.public.helpers`
2. Create partial template in `/templates/`
3. Handle both full page and partial responses
4. Add URL pattern to app's `urls.py`

### Adding API Endpoints
1. Create serializer in `apps/api/serializers/`
2. Create viewset/view in `apps/api/views/`
3. Write tests in `apps/api/tests/`
4. Add to `apps/api/urls.py`

### Integrating Third-Party Services
1. Add configuration to `settings/third_party.py`
2. Create integration module in `apps/integration/`
3. Define interface methods for the integration
4. Keep all integration logic isolated

## Migration Guidelines
- You are not yet trusted to manage migrations
- Do not create or run migrations without approval
- Wait for repository owner to handle migrations

## Documentation Reference

### Core Documentation (`docs/`)
Read these documents when working on specific areas:

#### Architecture & Design
- **ARCHITECTURE.md** - System design, app relationships, data flow
- **REPO_MAP.md** - Complete repository structure and file organization
- **MODEL_CONVENTIONS.md** - Model design patterns and naming standards
- **BEHAVIOR_MIXINS.md** - How to use and extend behavior mixins

#### Frontend Development
- **HTMX_INTEGRATION.md** - HTMX patterns, partial rendering, AJAX
- **TAILWIND_V4.md** - Tailwind CSS v4 configuration and usage
- **TEMPLATE_CONVENTIONS.md** - Template structure, inheritance, naming
- **VIEW_CONVENTIONS.md** - View patterns, MainContentView, HTMXView
- **MODAL_PATTERNS.md** - Modal implementation with HTMX

#### Error Handling & Testing
- **ERROR_HANDLING.md** - Error management strategies
- **advanced/TEST_CONVENTIONS.md** - Testing patterns and organization
- **advanced/E2E_TESTING.md** - End-to-end test implementation
- **advanced/BROWSER_TESTING.md** - Browser automation testing
- **advanced/TEST_TROUBLESHOOTING.md** - Common test issues and solutions

#### Setup & Configuration
- **guides/SETUP_GUIDE.md** - Detailed setup instructions
- **guides/CONTRIBUTING.md** - Contribution guidelines
- **guides/PYCHARM_CONFIG.MD** - PyCharm IDE configuration

#### Examples
- **examples/modal_example_view.py** - Modal view implementation
- **examples/item_list_example.html** - List view template
- **examples/list_items_partial.html** - HTMX partial template

### When to Read Documentation

1. **Before starting a new feature**: Read relevant architecture and convention docs
2. **When implementing models**: Review MODEL_CONVENTIONS.md and BEHAVIOR_MIXINS.md
3. **For frontend work**: Check HTMX_INTEGRATION.md and TEMPLATE_CONVENTIONS.md
4. **When writing tests**: Consult TEST_CONVENTIONS.md and relevant testing docs
5. **For troubleshooting**: Check ERROR_HANDLING.md and TEST_TROUBLESHOOTING.md
6. **Setting up development**: Follow SETUP_GUIDE.md

## Commit Guidelines
- Create detailed, focused commits
- Run formatters before committing: `black . && isort .`
- Check changes with `git status` before committing
- Don't include co-authors in commit messages
- do not document legacy systems
- do not document system migrations. only document new current state