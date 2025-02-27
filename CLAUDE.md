# Django Project Template - Development Guide

## Commands
- **Setup**: `python -m venv venv && source venv/bin/activate && pip install -r requirements/dev.txt`
- **Environment**: `cp .env.example .env.local` (then edit with your private keys)
- **Run server**: `python manage.py runserver`
- **Migrations**: `python manage.py makemigrations && python manage.py migrate`
- **Tests**: `python manage.py test apps.common.tests` (all tests in an app)
- **Single test**: `python manage.py test apps.common.tests.test_models.test_address.AddressModelTestCase`
- **Format code**: `black .`
- **Lint**: `flake8`

## Code Style
- **Python**: Follow PEP 8 and use Black formatter
- **Models**: Snake_case fields; boolean fields start with `is_/has_`; datetime fields end with `_at`
- **Methods**: Use verb phrases for methods, nouns for properties
- **Imports**: Django libraries first, third-party packages second, local imports last
- **Docstrings**: Required for models, complex functions, and behavior mixins
- **Error handling**: Be explicit with error messages; use custom assertion methods in tests
- **HTML/CSS**: Follow Django's templating conventions; use BEM for CSS classes
- **Environment Variables**: Store in `.env.local`, access with `os.environ.get()` with defaults

## Architecture
- Use behavior mixins (Timestampable, Authorable, etc.) from `apps.common.behaviors`
- Group code by app (common, api, public, communication, integration)
- Follow model conventions in `apps/common/models/CONVENTIONS.md`
- Document code thoroughly with meaningful docstrings