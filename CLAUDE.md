# Django Project Template - Development Guide

## Commands
- **Setup**: `python -m venv venv && source venv/bin/activate && pip install uv && ./requirements/install.sh dev`
- **Environment**: `cp .env.example .env.local` (then edit with your private keys)
- **Run server**: `python manage.py runserver`
- **Migrations**: `python manage.py makemigrations && python manage.py migrate`
- **Tests**: `DJANGO_SETTINGS_MODULE=settings pytest` (all tests in project)
- **Single test**: `DJANGO_SETTINGS_MODULE=settings pytest apps/common/tests/test_models/test_address.py::AddressModelTestCase -v`
- **Coverage**: `DJANGO_SETTINGS_MODULE=settings pytest --cov=apps`
- **HTML Coverage Report**: `DJANGO_SETTINGS_MODULE=settings pytest --cov=apps --cov-report=html`
- **XML Coverage Report**: `DJANGO_SETTINGS_MODULE=settings pytest --cov=apps --cov-report=xml` (for CI integrations)
- **Format code**: `black . && isort .`
- **Lint & type check**: `flake8 . && mypy .`

## Code Style
- **Python**: PEP 8 with Black formatter (line length 88); use type hints with mypy
- **Models**: Follow [behavior mixins](/apps/common/models/CONVENTIONS.md) pattern; datetime fields end with `_at`
- **Imports**: Group by standard lib, third-party, Django, local apps
- **Methods**: Verb phrases for methods, nouns for properties
- **HTMX**: Use `MainContentView` mixin for partial template rendering
- **Error handling**: Explicit error messages; form validation; use message framework
- **HTML/CSS**: Kebab-case for CSS classes, snake_case for ids; Tailwind for styling
- **Documentation**: Docstrings for models, complex functions, and behavior mixins

## Frontend Guidelines
- **HTMX**: Preferred for interactive functionality over JavaScript
- **JavaScript**: Only use inline attributes (onclick, etc.) when necessary
- **No Scripts**: Avoid adding `<script>` tags unless explicitly required
- **Tailwind CSS**: Use for styling instead of custom CSS where possible
- **Templates**: Place in root `/templates` directory, not in app directories

## Testing Practice
- **TDD Approach**: Write tests BEFORE implementing features
- **Database**: Never use SQLite for tests since app uses Postgres JSON fields
- **Organization**:
  - Model tests: `apps/{app_name}/tests/test_models/`
  - View tests: `apps/{app_name}/tests/test_views/`
  - Behavior tests: `apps/common/tests/test_behaviors/`
  - Factory classes: `apps/common/tests/factories.py`
- **Running Tests**:
  - Django tests: `DJANGO_SETTINGS_MODULE=settings pytest`
  - Behavior mixins: `python test_behaviors.py` (standalone tests)
  - With coverage: `DJANGO_SETTINGS_MODULE=settings pytest --cov=apps`
- **Python 3.12**: Use standalone behavior tests (`test_behaviors.py`) for Python 3.12 compatibility
- **Coverage**: 
  - Aim for 100% test coverage for models and behavior mixins
  - Use `.coveragerc` file to configure coverage settings and exclusions
  - Generate HTML reports with `--cov-report=html` for visual analysis
  - Check coverage in CI pipelines with `--cov-report=xml`

## Development Process
1. Check TODO.md to identify next priority item
2. Confirm feature implementation with team lead
3. Write tests covering all expected behaviors
4. Run tests to verify they fail (proving tests work correctly)
5. Implement just enough code to make tests pass
6. Refactor while keeping tests passing
7. Commit at logical milestones with descriptive messages
8. Update TODO.md with completed items

## Architecture
- Move away from component frameworks to standard Django templates
- Consolidate static files and templates to root directories
- Use uv for dependency management (transitioning from requirements files)
- Organize apps by domain (common, public, api, ai)