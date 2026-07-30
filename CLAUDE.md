# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Setup

```bash
python3 -m venv venv && source venv/bin/activate && pip install uv
uv sync --all-extras
cp .env.example .env.local  # set DATABASE_URL=postgres://$(whoami)@localhost:5432/django-project-template
createdb django-project-template
uv run python manage.py migrate
uv run python manage.py createsuperuser
# Alternative: ./requirements/setup.sh installs all dev dependencies
```

## Testing

- Tests require `DJANGO_SETTINGS_MODULE=settings` (e.g. `DJANGO_SETTINGS_MODULE=settings pytest`)
- **Never use SQLite** — this app relies on Postgres JSON fields
- Write tests before implementing (TDD); factories in `apps/common/tests/factories.py`; 100% coverage goal for models and behaviors
- E2E/visual tests run through `python tools/testing/browser_test_runner.py apps/**/tests/test_e2e_*.py` (or `test_visual_*.py`), not plain pytest

## Code Quality

- Formatting/linting/type-checking are pinned by `.pre-commit-config.yaml` (black, isort, flake8, bandit) — `uv run pre-commit run --all-files` is the source of truth, not ad hoc flags
- mypy is a dependency but disabled in pre-commit by default (slow); run manually with `uv run mypy .` when needed
- Datetime fields must end with `_at`

## Package Management

- **ONLY use uv** (`uv add`, `uv sync`) — never `pip install` or `uv pip install`
- Python >=3.12, dependencies in `pyproject.toml`

## Architecture Overview

See `docs/REPO_MAP.md` and `docs/ARCHITECTURE.md` for the full app/settings breakdown (also summarized in `/prime`). Notable conventions not obvious from the tree:
- Environment is selected by `DEPLOYMENT_TYPE` in `.env.local`, consumed by `settings/env.py`
- All templates live centrally under `/templates/` and all static assets under `/static/` — never per-app
- View classes: `MainContentView` for full pages, `HTMXView` for HTMX partials (`apps/public/views/helpers/`)

## Migrations

- Do not create or run migrations without approval — wait for the repository owner

## Documentation Reference

Read the matching doc in `docs/` before working in that area — see `docs/REPO_MAP.md` for the full index. Highlights: `MODEL_CONVENTIONS.md` / `BEHAVIOR_MIXINS.md` (models), `HTMX_INTEGRATION.md` / `TEMPLATE_CONVENTIONS.md` / `VIEW_CONVENTIONS.md` / `MODAL_PATTERNS.md` (frontend), `TEST_CONVENTIONS.md` / `TEST_TROUBLESHOOTING.md` / `guides/E2E_TESTING.md` / `guides/BROWSER_TESTING.md` (testing), `ERROR_HANDLING.md`.

## Documentation Philosophy

Document only the current state of the system. Never mention "old ways" or "previously" — delete outdated content rather than marking it deprecated, and completely rewrite docs to reflect current reality rather than layering changes on top.

## Commit Guidelines

- Detailed, focused commits; run `black . && isort .` before committing
- Don't include co-authors in commit messages

## Business Context

For business context, project notes, and assets see the work vault: `~/src/work-vault/Django Project Template/`
