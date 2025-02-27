
# Django Project Template

Technologies: Python, Django, PostgreSQL, 
API: Django Rest Framework
Web: HTMX, Tailwind CSS
Hosting: Render, AWS-S3
Integrations: 
    Transloadit for uploading and processing images
    SendGrid for email
    Stripe for payments
    OpenAI for GPTs
    Telegram for chatbot

## Quick Start Guide

Follow these steps to get this project up and running on your local machine:

### 1. Set up environment

```bash
# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install dependencies

```bash
# Install pip-tools
pip install pip-tools

# Generate and install requirements
pip-compile requirements/base.in -o requirements/base.txt
pip-compile requirements/dev.in -o requirements/dev.txt
pip-compile requirements/prod.in -o requirements/prod.txt

# Install development dependencies
pip install -r requirements/dev.txt
```

### 3. Configure local settings

```bash
# Copy the local settings template
cp settings/local_template.py settings/local.py

# Copy the environment variables example file
cp .env.example .env.local

# Edit .env.local:
# - Add your secure SECRET_KEY (50 characters)
# - Configure your PostgreSQL database settings
# - Add API keys and other sensitive information
```

### 4. Set up the database

```bash
# Create a PostgreSQL database
createdb your_database_name  # Or use your preferred PostgreSQL client

# Run migrations
python manage.py migrate
```

### 5. Create a superuser and run server

```bash
# Create admin user
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

Visit http://127.0.0.1:8000/ to see your application running!

### Alternative: Using Docker

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


# Project Structure

This project is structured in a modular fashion to promote separation of concerns and maintainability. Below is the directory structure along with descriptions for each major module:

- `apps/`: Contains all applications that make up the project.
- `settings/`: Configuration settings for the entire Django project.
- `static/`: Global static files such as CSS, JS, and images.
- `templates/`: Global HTML templates.
- `build.sh`: Build script for Render deployment
- `requirements.txt`: Lists all Python dependencies.
- `runtime.txt`: Specifies the Python runtime.

### API

_Defines the application programming interface (API) layer, responsible for handling all the RESTful requests._

- `apps/api/`: api app 
  - `serializers/`: Contains serializer classes for converting complex data types to JSON.
  - `tests/`: Holds test cases for the API application.
  - `views/`: Contains views that manage the logic and control flow for API requests.
  - `urls.py`: URL declarations for API routes. 

### Common

_General purpose and shared components for any applications. 
This includes models, forms, views, and other components that are shared across multiple apps._

_Key Features include 1. Enhanced User model with best practices for consumer-facing apps. 2. Common model behaviors like timestamping, authoring, etc. 3. Large collection of utility functions for common problems encountered while building applications._


- `apps/common/`: common app
  - `behaviors/`: Common model behaviors like timestamping.
  - `forms/`: Shared form definitions.
  - `migrations/`: Database migration scripts for common models.
  - `models/`: General purpose model definitions.
  - `serializers/`: Common serializer classes.
  - `tests/`: Tests for common functionality.
  - `utilities/`: Helper functions and classes.
  - `views/`: Shared views.
  - `admin.py`: Admin interface configurations.

### Communication

_Contains all communication-related modules and integration-specific logic. 
Each type of communication has a model: SMS, Email, etc_

- `apps/communication/`: communication app 
  - `forms/`: Form definitions for the communication app.
  - `migrations/`: Migration scripts for communication-related models.
  - `models/`: Data models specific to communication.
  - `static/`: Static files for the communication module.
  - `templates/`: HTML templates for the communication module.
  - `tests/`: Tests for communication features.
  - `views/`: Views handling communication flows.
  - `admin.py`: Admin configurations for communication.
  - `apps.py`: Application settings for communication.
  - `urls.py`: URL patterns for communication features.

### Integration

_Contains all integration-specific logic and modules. Each integration is a separate module within this directory.
Keep all integration-specific logic within the integration definitions here.
When 3rd party APIs or SD are updated, the integration modules should be updated accordingly.
Define your own interface methods for each integration module and call them from the other apps._

- `apps/integration/`: Integrations with external services.
  - `slack/`: Slack integration components.
  - `telegram/`: Telegram bot components.

### Public

_Contains all modules and logic to power UI served by this system. This includes the websites, landing pages, and any other public-facing components.
Remove this app if you don't need a public-facing website. Note this is separate from the built-in Django admin interface._

- `apps/public/`: Public-facing components of the project.
  - `components/`: Reusable components for the frontend.
  - `middleware/`: Middleware for handling requests/responses.
  - `static/`: Static assets for the public module.
  - `templates/`: HTML templates for the public views.
  - `views/`: Views serving the public-facing parts of the project.
  - `__init__.py`: Initialization file for the public module.
  - `urls.py`: URL patterns for the public section.

