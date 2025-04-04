# Django Project Template - Development Guide

This guide complements the main [README.md](README.md) and provides specific instructions for developers contributing to this project. For project overview, structure, and features, see the [README.md](README.md).

## Package Management
- **ONLY use uv**: For all package and dependency management
- **Installation**: `uv add package`
- **Run tools**: `uv run tool`
- **Upgrading packages**: `uv add --dev package --upgrade-package package`
- **FORBIDDEN**: `uv pip install`, `@latest` syntax

## Commands
- **Setup**: `python -m venv venv && source venv/bin/activate && pip install uv && ./requirements/install.sh dev`
- **Environment**: `cp .env.example .env.local` (then edit with your private keys)
- **Run server**: `python manage.py runserver`
- **Migrations**: `python manage.py makemigrations && python manage.py migrate`

### Testing Commands
- **Run all tests**: `DJANGO_SETTINGS_MODULE=settings pytest`
- **Single test file**: `DJANGO_SETTINGS_MODULE=settings pytest apps/common/tests/test_models/test_address.py -v`
- **Single test class**: `DJANGO_SETTINGS_MODULE=settings pytest apps/common/tests/test_models/test_address.py::AddressModelTestCase -v`
- **Single test method**: `DJANGO_SETTINGS_MODULE=settings pytest apps/common/tests/test_models/test_address.py::AddressModelTestCase::test_string_representation -v`
- **Run tests by keyword**: `DJANGO_SETTINGS_MODULE=settings pytest -k "user and not stripe" -v`
- **Run with detailed errors**: `DJANGO_SETTINGS_MODULE=settings pytest -vxs`
- **Run only failing tests**: `DJANGO_SETTINGS_MODULE=settings pytest --failed-first`
- **Coverage**: `DJANGO_SETTINGS_MODULE=settings pytest --cov=apps`
- **HTML Coverage Report**: `DJANGO_SETTINGS_MODULE=settings pytest --cov=apps --cov-report=html:apps/common/tests/coverage_html_report`
- **XML Coverage Report**: `DJANGO_SETTINGS_MODULE=settings pytest --cov=apps --cov-report=xml:apps/common/tests/coverage.xml` (for CI integrations)

### Code Quality
- **Format code**: `black . && isort .`
- **Lint & type check**: `flake8 . && mypy .`

## Code Style
- **Python**: PEP 8 with Black formatter (line length 88); use type hints with mypy
- **Models**: Follow [behavior mixins](docs/MODEL_CONVENTIONS.md) pattern; datetime fields end with `_at`
  - See [README.md](README.md#behavior-mixins) for full list of available behavior mixins
- **Imports**: Group by standard lib, third-party, Django, local apps
- **Methods**: Verb phrases for methods, nouns for properties
- **HTMX**: Use `HTMXView` for HTMX-specific views and `MainContentView` for standard pages
- **Error handling**: Explicit error messages; form validation; use message framework
- **HTML/CSS**: Kebab-case for CSS classes, snake_case for ids; Tailwind for styling
- **Documentation**: Docstrings for models, complex functions, and behavior mixins
- **Functions**: Must be focused and small (single responsibility)
- **Type hints**: Required for all code
- **Formatting guidelines**:
  - Line length: 88 chars maximum
  - Strings: use parentheses for line wrapping
  - Function calls: multi-line with proper indentation
  - Imports: split into multiple lines when needed

## Frontend Guidelines
- **HTMX**: Preferred for interactive functionality over JavaScript
- **View Classes**:
  - Use `MainContentView` for standard pages (from `apps.public.helpers`)
  - Use `HTMXView` for HTMX-specific components (from `apps.public.helpers`)
  - Add `TeamSessionMixin` when team context is needed
- **JavaScript**: Only use inline attributes (onclick, etc.) when necessary
- **No Scripts**: Avoid adding `<script>` tags unless explicitly required
- **Tailwind CSS v4**: Use for styling with django-tailwind-cli instead of custom CSS where possible
- **Templates**: Place in root `/templates` directory, not in app directories

For detailed conventions on templates and views, see:
- [Template Conventions](docs/TEMPLATE_CONVENTIONS.md)
- [View Conventions](docs/VIEW_CONVENTIONS.md)

## Testing Practice
- **TDD Approach**: Write tests BEFORE implementing features
- **Database**: Never use SQLite for tests since app uses Postgres JSON fields
- **Test Categories**:
  - **Unit Tests**: Test individual functions, classes, or small components
  - **Integration Tests**: Test interactions between components
  - **E2E Tests**: Test complete user workflows with browser automation
  - **Visual Tests**: Test the visual appearance of UI components
  - **API Tests**: Test REST API endpoints and responses
- **Organization**:
  - Model tests: `apps/{app_name}/tests/test_models/`
  - View tests: `apps/{app_name}/tests/test_views/`
  - Behavior tests: `apps/common/tests/behaviors.py` (consolidated approach with both database and direct tests)
  - E2E tests: `apps/{app_name}/tests/test_e2e_*.py`
  - Visual tests: `apps/{app_name}/tests/test_visual_*.py`
  - Factory classes: `apps/common/tests/factories.py`
- **Running Tests**:
  - All tests: `./test.sh`
  - Specific type: `./test.sh --type unit|integration|e2e|visual|api`
  - With coverage: `./test.sh --coverage`
  - With HTML report: `./test.sh --html-report`
  - Browser tests: `./test.sh --browser --no-headless`
  - For detailed test management: `python tools/testing/test_manager.py run|list|report --category all|unit|integration|e2e|visual|api`
- **Browser Testing**:
  - E2E tests: `python tools/testing/browser_test_runner.py apps/**/tests/test_e2e_*.py`
  - Visual tests: `python tools/testing/browser_test_runner.py apps/**/tests/test_visual_*.py`
- **Python 3.12**: Use standalone behavior tests (`apps/common/behaviors/tests/test_behaviors.py`) for Python 3.12 compatibility
- **Coverage**: 
  - Aim for 100% test coverage for models and behavior mixins
  - Generate HTML reports with `./test.sh --html-report`
  - Check coverage in CI pipelines with `./test.sh --xml-report`
- **Test Requirements**:
  - New features require tests
  - Bug fixes must include regression tests
  - Test edge cases and error conditions
  - For async code, use anyio (not asyncio)
  - Use pytest markers to categorize tests (e.g., `@pytest.mark.e2e`)

## Documentation
- [README.md](README.md) - Project overview, features and structure
- [docs/SETUP_GUIDE.md](docs/SETUP_GUIDE.md) - Detailed setup instructions
- [docs/CONTRIBUTING.md](docs/guides/CONTRIBUTING.md) - Contribution guidelines
- [docs/TODO.md](docs/TODO.md) - Current tasks and priorities
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) - Project architecture and app relationships
- [docs/BEHAVIOR_MIXINS.md](docs/BEHAVIOR_MIXINS.md) - Details on behavior mixins
- [docs/MODEL_CONVENTIONS.md](docs/MODEL_CONVENTIONS.md) - Model conventions
- [docs/TEMPLATE_CONVENTIONS.md](docs/TEMPLATE_CONVENTIONS.md) - Template guidelines and patterns
- [docs/VIEW_CONVENTIONS.md](docs/VIEW_CONVENTIONS.md) - View classes and HTMX integration
- [docs/TEST_CONVENTIONS.md](docs/TEST_CONVENTIONS.md) - Testing practices and organization

## Development Process
1. Check [docs/TODO.md](docs/TODO.md) to identify next priority item
2. Think deeply to plan out next steps and how to implement the feature
3. Write tests covering all expected behaviors
4. Run tests to verify they fail (proving tests work correctly)
5. Implement just enough code to make tests pass
6. Commit changes to your working branch
7. Review and Refactor your work. Simplify if possible without sacrificing functionality
8. Commit changes when all tests are passing
9. Continue to achieve 100% test coverage
10. Update [docs/TODO.md](docs/TODO.md) with updated plans and marking items completed when they have 100% test coverage

## Commit Guidelines
- Create detailed, focused commits
- Run code formatters before committing
- Check all changes with `git status` before committing
- Don't include co-authors in commit messages

## Architecture
- Move away from component frameworks to standard Django templates
- Consolidate static files and templates to root directories
- Use uv for dependency management
- Organize apps by domain (common, public, api, ai, integrations)

## Code Quality Tools
- **Ruff**: Code formatting and linting
  - Format: `uv run ruff format .`
  - Check: `uv run ruff check .`
  - Fix: `uv run ruff check . --fix`
- **Type Checking**:
  - Tool: `uv run pyright`
  - Requirements:
    - Explicit None checks for Optional
    - Type narrowing for strings

For detailed project structure and app descriptions, refer to:
- [Project Structure](README.md#project-structure) section in the README
- [Architecture Document](docs/ARCHITECTURE.md) for a visual overview and app relationships

## Key Technology Documentation
- **Django**: https://docs.djangoproject.com/en/5.0/
- **Django REST Framework**: https://www.django-rest-framework.org/
- **HTMX**: https://htmx.org/docs/
- **Tailwind CSS v4**: https://tailwindcss.com/docs
- **Unfold Admin**: https://unfoldadmin.com/docs/
- **Pytest Django**: https://pytest-django.readthedocs.io/en/latest/
- **Browser-Use**: https://pypi.org/project/browser-use/
- **uv Package Manager**: https://docs.astral.sh/uv/
- **Ruff Linter**: https://docs.astral.sh/ruff/
- **MCP Python SDK** https://raw.githubusercontent.com/modelcontextprotocol/python-sdk/refs/heads/main/README.md
