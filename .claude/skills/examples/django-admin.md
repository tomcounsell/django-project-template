---
name: django-admin
description: Common Django admin and management commands for this project
triggers:
  - "run migrations"
  - "create superuser"
  - "collect static"
  - "django shell"
  - "manage.py"
---

# Django Admin Skill

## Management Commands

### Development
```bash
uv run python manage.py runserver           # Start dev server
uv run python manage.py shell               # Django shell (IPython)
uv run python manage.py dbshell             # PostgreSQL shell
```

### Database
```bash
uv run python manage.py makemigrations      # Create migrations
uv run python manage.py migrate             # Apply migrations
uv run python manage.py showmigrations      # Show migration status
```

### Users
```bash
uv run python manage.py createsuperuser     # Create admin user
uv run python manage.py changepassword <user>  # Reset password
```

### Static Files
```bash
uv run python manage.py collectstatic --noinput  # Collect static files
uv run python manage.py tailwind build           # Build Tailwind CSS
```

### Data
```bash
uv run python manage.py dumpdata app.Model --indent 2 > fixture.json
uv run python manage.py loaddata fixture.json
```

### Debugging
```bash
uv run python manage.py check               # Run system checks
uv run python manage.py show_urls           # List all URL patterns (django-extensions)
uv run python manage.py shell_plus          # Enhanced shell (django-extensions)
```

## Testing
```bash
DJANGO_SETTINGS_MODULE=settings pytest                    # All tests
DJANGO_SETTINGS_MODULE=settings pytest apps/common/ -v    # Specific app
DJANGO_SETTINGS_MODULE=settings pytest -k "test_user" -v  # By keyword
```

## Code Quality
```bash
uv run black . && uv run isort --profile black .  # Format
uv run ruff check . --fix                          # Lint + autofix
```
