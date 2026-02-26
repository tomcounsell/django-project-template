---
name: deployment
description: Deployment checklist and procedures
triggers:
  - "deploy"
  - "release"
  - "production"
  - "go live"
---

# Deployment Skill

## Pre-Deployment Checklist

1. **Tests pass**: `DJANGO_SETTINGS_MODULE=settings pytest`
2. **Code formatted**: `uv run black . && uv run isort --profile black .`
3. **Lint clean**: `uv run ruff check .`
4. **No pending migrations**: `uv run python manage.py showmigrations | grep "\[ \]"`
5. **Static files collected**: `uv run python manage.py collectstatic --noinput`
6. **Environment variables set**: Check `.env.example` against production config
7. **Dependencies locked**: `uv lock` and commit `uv.lock`

## Environment Variables

Required in production (see `.env.example`):
- `SECRET_KEY` - Django secret key (generate a new one)
- `DATABASE_URL` - PostgreSQL connection string
- `DEPLOYMENT_TYPE` - Set to `PRODUCTION`
- `DEBUG` - Must be `False`
- `ALLOWED_HOSTS` - Comma-separated list of domains

## Database Migrations

```bash
# Review pending migrations
uv run python manage.py showmigrations

# Apply in production
uv run python manage.py migrate --no-input
```

## Static Files

```bash
# Build Tailwind and collect static
uv run python manage.py tailwind build
uv run python manage.py collectstatic --noinput
```

## Health Check

After deployment, verify:
1. Admin page loads: `https://your-domain.com/admin/`
2. API responds: `https://your-domain.com/api/`
3. Static files served correctly
4. Database connections working
