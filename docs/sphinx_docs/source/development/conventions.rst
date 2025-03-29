Code Conventions
===============

This project follows specific conventions to ensure consistency and maintainability.

Python Style
-----------

- Follow PEP 8 with Black formatter (line length 88)
- Use type hints with mypy
- Group imports in this order:
  1. Standard library imports
  2. Third-party imports
  3. Django imports
  4. Local app imports
- Use verb phrases for methods, nouns for properties
- Use descriptive variable names
- Add docstrings to classes and complex functions

Models
------

- Follow behavior mixin pattern
- Use explicit `related_name` for relationships
- DateTime fields end with `_at` (e.g., `created_at`)
- Boolean fields start with `is_`, `has_`, or `can_`
- Add docstrings to models and complex fields
- Include appropriate Meta options for ordering, permissions

Views
-----

- Use appropriate class-based views
- For HTMX components, extend `HTMXView`
- For full pages, extend `MainContentView`
- Add team context with `TeamSessionMixin` when needed
- Return appropriate status codes
- Handle errors explicitly

Templates
--------

- Use kebab-case for CSS classes
- Use snake_case for template variables and ids
- Structure templates with clear blocks
- Include only what's needed via `{% include %}`
- Use partials for HTMX responses

JavaScript
---------

- Minimize JavaScript usage
- Prefer HTMX attributes in HTML
- Use HTML data attributes for configuration
- Keep scripts in base.js when necessary

Testing
------

- Name test classes with `TestCase` suffix
- Name test methods with `test_` prefix
- Use factories for creating test objects
- Mock external services
- Use pytest fixtures for common setups