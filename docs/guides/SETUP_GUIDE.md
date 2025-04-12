# Django Project Template: Developer Setup Guide

This guide provides detailed instructions for setting up the Django Project Template on your local development environment.

## Prerequisites

Before you begin, ensure you have the following installed on your machine:

- Python 3.9+ (recommend 3.12)
- Git
- PostgreSQL 14+
- Node.js 18+ and npm (for frontend assets)

## Automated Setup (Recommended)

The project includes an automated setup script that handles most of the setup process for you:

```bash
# Clone the main repository
git clone https://github.com/yudame/django-project-template.git

# Change to the project directory
cd django-project-template

# Make the setup script executable
chmod +x setup_local_env.sh

# Run the setup script (with source to enable virtual environment activation)
source setup_local_env.sh
```

The setup script will:
1. Check prerequisites (Python, PostgreSQL, Node.js)
2. Set up a Python virtual environment
3. Install dependencies
4. Create configuration files
5. Set up the database
6. Run migrations
7. Prompt to create a superuser
8. Set up frontend dependencies

The script is idempotent, so it's safe to run multiple times. It tracks progress in a `.setup_progress` file to avoid repeating steps unnecessarily.

## Manual Setup

If you prefer to set up manually or need more control over the process, follow these steps:

### Step 1: Clone the Repository

```bash
# Clone the main repository
git clone https://github.com/yudame/django-project-template.git

# Change to the project directory
cd django-project-template

# Optional: Add the original repository as upstream remote for future updates
git remote add upstream https://github.com/yudame/django-project-template.git

# Verify remotes
git remote -v
```

Setting up the upstream remote allows you to fetch future improvements to the template:

```bash
# Fetch updates from the upstream repository
git fetch upstream

# View new commits on main branch
git log main..upstream/main

# Selectively apply specific improvements
git cherry-pick <commit-hash>
```

### Step 2: Set Up Python Environment and Dependencies

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On macOS/Linux
source venv/bin/activate
# On Windows
# venv\Scripts\activate

# Install uv (fast dependency installer)
pip install uv

# Install all project dependencies
./requirements/install.sh dev
```

### Step 3: Set Up Environment Variables

```bash
# Copy the local settings template
cp settings/local_template.py settings/local.py

# Copy the environment variables example file
cp .env.example .env.local

# Edit the file with your specific configuration
nano .env.local  # or use your preferred editor
```

Important environment variables to configure in your `.env.local` file:

- `DEBUG`: Set to `True` for development
- `SECRET_KEY`: A random string (50 characters) for crypto operations
- `DATABASE_URL`: PostgreSQL connection string (or DB_NAME, DB_USER, etc.)
- `DJANGO_SETTINGS_MODULE`: Set to `settings` for development
- AWS credentials (if using S3)
- Third-party integration keys (Loops, Supabase, etc.)
- Social authentication credentials

### Step 4: Database Setup

```bash
# Create a PostgreSQL database
createdb django_project_template

# Run migrations to set up the database schema
python manage.py migrate
```

### Step 5: Create Superuser

```bash
# Create an admin user
python manage.py createsuperuser
```

### Step 6: Run the Development Server

```bash
# Start the Django development server
python manage.py runserver
```

The site should now be accessible at `http://127.0.0.1:8000/`

### Step 7: Frontend Setup (if needed)

```bash
# Install frontend dependencies
npm install

# Run Tailwind CSS in watch mode
npm run watch:css
```

## Alternative: Using Docker

If you prefer to use Docker for development:

```bash
# Create a .env.local file from the example
cp .env.example .env.local

# Build and start the containers
docker-compose up -d

# Create a superuser
docker-compose exec web python manage.py createsuperuser
```

Visit http://127.0.0.1:8000/ to see your Docker-based application running.

## Common Development Tasks

### Running Tests

```bash
# Run all tests
DJANGO_SETTINGS_MODULE=settings pytest

# Run specific test file or module
DJANGO_SETTINGS_MODULE=settings pytest apps/common/tests/test_models/test_user.py

# Run a specific test case
DJANGO_SETTINGS_MODULE=settings pytest apps/common/tests/test_models/test_user.py::UserModelTestCase

# Run tests with coverage report
DJANGO_SETTINGS_MODULE=settings pytest --cov=apps --cov-report=html
```

### Creating Migrations

```bash
# Create new migrations for app changes
python manage.py makemigrations

# Apply migrations to database
python manage.py migrate

# Show migration status
python manage.py showmigrations
```

### Code Quality and Formatting

```bash
# Format your code with Black and isort
black .
isort .

# Run linting and type checking
flake8 .
mypy .
```

### Working with Git

```bash
# Create a new feature branch
git checkout -b feature/new-feature-name

# Add and commit changes
git add .
git commit -m "Add detailed description of changes"

# Push branch to remote
git push -u origin feature/new-feature-name

# Create a pull request (on GitHub website)
```

### Deployment

For deployments to platforms like Render or Heroku:

```bash
# Generate the requirements.txt file needed for deployment
./requirements/generate_deployment_requirements.sh

# This will create a requirements.txt file in the project root 
# which can be used by deployment platforms
```

## Project Structure Overview

### Key Directories

- `apps/`: Main application code, organized by domains
  - `common/`: Shared models, utilities, and behaviors
  - `public/`: User-facing views and templates
  - `api/`: REST API endpoints and serializers
  - `ai/`: AI-related functionality
- `settings/`: Project configuration
- `templates/`: Global templates
- `static/`: Static files (CSS, JS, images)
- `requirements/`: Dependency management

### Behavior Mixins

The project uses behavior mixins to add common functionality to models. For detailed examples of how to use behavior mixins, see the `BlogPost` model in `apps/common/models/blog_post.py`, which demonstrates all available behaviors in a real-world example.

## Troubleshooting

### Database Connection Issues

If you encounter problems connecting to the database:
1. Verify PostgreSQL is running: `pg_isready`
2. Check your database URL in `.env.local`
3. Ensure the database exists: `psql -c '\l'`

### Missing Migrations

If you get a "no migrations to apply" message but the database doesn't have your models:
1. Check if your models are registered in the app's `__init__.py`
2. Run `python manage.py makemigrations <app_name>`
3. Check the generated migration file

### Test Failures

1. Make sure you're using the correct settings: `DJANGO_SETTINGS_MODULE=settings`
2. Check if dependencies are installed: `pip install -r requirements/dev.lock.txt`
3. Verify the test database can be created by your user

## Getting Help

If you need assistance:
1. Check the project documentation in the `docs/` directory
2. Look at the model implementation examples in `apps/common/models/`
3. Refer to the test cases for usage examples
4. Contact the project maintainers

## Next Steps

After setting up your development environment:
1. Review the architecture and code conventions in [CONTRIBUTING.md](CONTRIBUTING.md)
2. Explore the behavior mixins in `apps/common/behaviors/`
3. Look at existing models to understand patterns and conventions
4. Read up on HTMX integration for adding interactive frontend features
5. Check the [TODO.md](TODO.md) file to identify areas where you can contribute