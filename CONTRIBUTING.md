# Contributing to Django Project Template

Thank you for your interest in contributing to this Django project template! This document provides guidelines to ensure code quality and consistency.

## Development Philosophy

1. **Test-Driven Development**: We aim for 100% test coverage, starting with models and behavior mixins
2. **Clean Architecture**: Keep code modular with clear separation of concerns
3. **Simplicity Over Complexity**: Prefer simple, standard Django patterns over custom frameworks
4. **Documentation**: Document everything, especially behavior mixins and model conventions

## Getting Started

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/django-project-template.git
   cd django-project-template
   ```

2. **Set up the environment**
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements/dev.txt
   cp .env.example .env.local  # Edit with your private keys
   ```

3. **Run migrations and start the server**
   ```bash
   python manage.py migrate
   python manage.py runserver
   ```

4. **Create a feature branch**
   ```bash
   git checkout -b feature/descriptive-name
   ```

## Development Workflow

### Code Style and Quality

- Run formatter and linter before committing:
  ```bash
  black . && isort . && flake8 . && mypy .
  ```
- Use type hints for all function parameters and return values
- Follow the model conventions in `apps/common/models/CONVENTIONS.md`
- Group imports: standard library, third-party, Django, local apps

### Testing

- Write tests before implementing features
- Run tests with coverage reporting:
  ```bash
  pytest --cov=apps
  ```
- Test isolated units with proper mocking
- For behavior mixins, create tests that verify all functionality
- For model tests, verify field constraints and model methods

### Directory Structure

- Place templates in the root `templates/` directory
- Place static files in the root `static/` directory
- Organize apps by domain (common, public, api, etc.)
- Use behavior mixins from `apps.common.behaviors`

## Model Development

1. **Use Behavior Mixins**: Inherit from appropriate mixins in `apps.common.behaviors`
2. **Follow Naming Conventions**:
   - Boolean fields: start with `is_` or `has_`
   - Datetime fields: end with `_at`
   - Properties: nouns reflecting the value returned
   - Methods: verb phrases describing the action

3. **Document Models**:
   - Add docstrings explaining model purpose
   - List key attributes and properties
   - Document special behaviors

## Pull Request Process

1. **Ensure all tests pass** with 100% coverage for your changes
2. **Update documentation** relevant to your changes
3. **Add your changes to the CHANGELOG.md** under Unreleased section
4. **Create a pull request** with a clear description of changes
5. **Address reviewer feedback** promptly

## Commit Messages

- Use the imperative mood ("Add feature" not "Added feature")
- First line: summary (50 chars max)
- Followed by blank line and detailed explanation if needed
- Reference issues: "Fixes #123" or "Relates to #456"

## High Priority Contributions

See [TODO.md](TODO.md) for our current priorities, especially:
1. Improving test coverage
2. Template and static file consolidation
3. Removing component framework dependencies
4. Implementing uv for dependency management
5. App restructuring
6. Team model implementation

Thank you for contributing to making this project better!