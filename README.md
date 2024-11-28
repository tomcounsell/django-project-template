
Technologies: Python, Django, PostgreSQL, 
API: Django Rest Framework
Web: HTMX, Bulma CSS
Hosting: Heroku or Render, AWS-S3
Integrations: 
    Transloadit for uploading and processing images
    SendGrid for email
    Stripe for payments
    OpenAI for GPTs
    Telegram for chatbot


# Project Structure

This project is structured in a modular fashion to promote separation of concerns and maintainability. Below is the directory structure along with descriptions for each major module:

- `apps/`: Contains all applications that make up the project.
- `settings/`: Configuration settings for the entire Django project.
- `static/`: Global static files such as CSS, JS, and images.
- `templates/`: Global HTML templates.
- `Procfile`: Specifies startup services for Heroku
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

