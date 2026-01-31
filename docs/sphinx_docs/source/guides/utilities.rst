==========================
Common Utilities Collection
==========================

The ``apps/common/utilities/`` directory contains a comprehensive collection of helper functions, classes, and utilities that solve common problems in Django development. These utilities go well beyond Django's built-in functionality, providing production-ready solutions for logging, forms, screenshots, text processing, and more.

.. contents:: Table of Contents
   :local:
   :depth: 2

Overview
========

Purpose
-------

Centralized utilities provide:

- **Consistency**: Standardized approaches to common problems
- **DRY Principle**: Reusable code across applications
- **Best Practices**: Production-tested patterns
- **Time Savings**: Pre-built solutions to frequent challenges

Organization
------------

Utilities are organized into the following modules:

.. code-block:: text

   apps/common/utilities/
   ├── logger.py              # Logging and error handling
   ├── forms.py               # Form validation utilities
   ├── screenshots.py         # Screenshot capture service
   ├── email.py               # Email utilities
   ├── database/              # Database helpers
   │   ├── db.py
   │   └── model_fields.py
   ├── processing/            # Data processing utilities
   │   ├── multithreading.py
   │   ├── regex.py
   │   ├── unicode_tools.py
   │   ├── serializers.py
   │   └── english_language.py
   ├── django/                # Django-specific utilities
   │   ├── backends.py
   │   └── middleware.py
   ├── drf_permissions/       # DRF permission classes
   │   └── api_key.py
   └── compression/           # Image compression
       └── image_compression.py

Import Conventions
------------------

Import utilities directly from their modules:

.. code-block:: python

   # Logger utilities
   from apps.common.utilities.logger import (
       AppError,
       ValidationError,
       log_error,
       error_decorator,
   )

   # Form utilities
   from apps.common.utilities.forms import (
       FormValidationMixin,
       BaseModelForm,
       validate_form_data,
   )

   # Processing utilities
   from apps.common.utilities.processing.english_language import (
       build_english_list,
   )

Logger & Error Handling
=======================

The ``logger.py`` module provides standardized logging and error handling for the entire project, ensuring consistent error reporting, formatting, and handling across all applications.

Exception Classes
-----------------

AppError
~~~~~~~~

Base exception class for application-specific errors.

.. code-block:: python

   from apps.common.utilities.logger import AppError

   class AppError(Exception):
       """Base exception with structured error information.

       Attributes:
           message (str): Human-readable error message
           code (str): Machine-readable error code
           status_code (int): HTTP status code to return
           details (Dict): Additional error details
       """

**Usage Example:**

.. code-block:: python

   from apps.common.utilities.logger import AppError

   def process_payment(amount):
       if amount <= 0:
           raise AppError(
               message="Invalid payment amount",
               code="invalid_amount",
               status_code=400,
               details={"amount": amount, "min_amount": 0.01}
           )

ValidationError
~~~~~~~~~~~~~~~

Exception raised for data validation errors with field-level details.

.. code-block:: python

   from apps.common.utilities.logger import ValidationError

   def validate_user_data(data):
       field_errors = {}

       if not data.get('email'):
           field_errors['email'] = ['Email is required']

       if not data.get('username') or len(data['username']) < 3:
           field_errors['username'] = ['Username must be at least 3 characters']

       if field_errors:
           raise ValidationError(
               message="User data validation failed",
               field_errors=field_errors
           )

AuthenticationError
~~~~~~~~~~~~~~~~~~~

Exception for authentication failures (401 responses).

.. code-block:: python

   from apps.common.utilities.logger import AuthenticationError

   def verify_token(token):
       if not token or not is_valid_token(token):
           raise AuthenticationError(
               message="Invalid or expired token",
               code="invalid_token"
           )

PermissionError
~~~~~~~~~~~~~~~

Exception for authorization failures (403 responses).

.. code-block:: python

   from apps.common.utilities.logger import PermissionError

   def check_resource_access(user, resource):
       if resource.owner != user:
           raise PermissionError(
               message="You don't have permission to access this resource",
               details={"resource_id": resource.id}
           )

NotFoundError
~~~~~~~~~~~~~

Exception for resource not found (404 responses).

.. code-block:: python

   from apps.common.utilities.logger import NotFoundError
   from django.shortcuts import get_object_or_404

   def get_user_profile(user_id):
       try:
           return UserProfile.objects.get(id=user_id)
       except UserProfile.DoesNotExist:
           raise NotFoundError(
               message="User profile not found",
               details={"user_id": user_id}
           )

ConflictError
~~~~~~~~~~~~~

Exception for resource conflicts like duplicate entries (409 responses).

.. code-block:: python

   from apps.common.utilities.logger import ConflictError

   def create_username(username):
       if User.objects.filter(username=username).exists():
           raise ConflictError(
               message="Username already exists",
               code="username_taken",
               details={"username": username}
           )

Logging Functions
-----------------

log_error()
~~~~~~~~~~~

Log exceptions with consistent formatting and contextual information.

.. code-block:: python

   from apps.common.utilities.logger import log_error

   def log_error(
       exc: Exception,
       request: HttpRequest | None = None,
       level: int = logging.ERROR,
       include_traceback: bool = True,
   ) -> None:
       """Log an exception with context.

       Args:
           exc: The exception to log
           request: Optional HTTP request that caused the exception
           level: Logging level (ERROR, WARNING, INFO, DEBUG)
           include_traceback: Whether to include full traceback
       """

**Usage Example:**

.. code-block:: python

   from apps.common.utilities.logger import log_error
   import logging

   def process_data(request, data):
       try:
           # Process data
           result = complex_operation(data)
       except ValueError as e:
           # Log with request context
           log_error(e, request, level=logging.WARNING)
           return None
       except Exception as e:
           # Log critical errors with full traceback
           log_error(e, request, level=logging.ERROR, include_traceback=True)
           raise

Error Handling Decorators
--------------------------

error_decorator
~~~~~~~~~~~~~~~

Decorator to handle exceptions in view functions automatically.

.. code-block:: python

   from apps.common.utilities.logger import error_decorator

   @error_decorator
   def my_view(request):
       # View code that might raise exceptions
       user_data = get_user_data(request.user.id)

       if not user_data:
           raise NotFoundError("User data not found")

       return render(request, 'profile.html', {'data': user_data})

**Features:**

- Catches all exceptions in the view
- Logs them with request context
- Returns appropriate error responses (JSON for API, HTML for web)
- Handles HTMX requests with partial templates

ErrorHandlingMixin
~~~~~~~~~~~~~~~~~~

Mixin for class-based views with automatic error handling.

.. code-block:: python

   from apps.common.utilities.logger import ErrorHandlingMixin
   from django.views import View

   class MyView(ErrorHandlingMixin, View):
       def get(self, request):
           # View code with automatic error handling
           data = self.get_data()
           return render(request, 'template.html', {'data': data})

       def get_data(self):
           # This will be caught and handled automatically
           if not self.request.user.is_authenticated:
               raise AuthenticationError("Login required")

Response Helpers
----------------

handle_view_exception()
~~~~~~~~~~~~~~~~~~~~~~~

Handle exceptions in Django views with consistent error responses.

.. code-block:: python

   from apps.common.utilities.logger import handle_view_exception

   def my_view(request):
       try:
           # View logic
           return render(request, 'template.html')
       except Exception as exc:
           return handle_view_exception(exc, request)

**Response Types:**

- **JSON**: For AJAX/API requests
- **HTML**: For standard browser requests
- **HTMX**: Partial templates for HTMX requests

api_exception_handler()
~~~~~~~~~~~~~~~~~~~~~~~~

DRF exception handler for consistent API error responses.

Configure in ``settings.py``:

.. code-block:: python

   REST_FRAMEWORK = {
       'EXCEPTION_HANDLER': 'apps.common.utilities.logger.api_exception_handler',
   }

**Example Response:**

.. code-block:: json

   {
       "error": "Invalid email address",
       "code": "validation_error",
       "status_code": 400,
       "field_errors": {
           "email": ["Enter a valid email address"]
       }
   }

Integration Examples
--------------------

In Views
~~~~~~~~

.. code-block:: python

   from apps.common.utilities.logger import error_decorator, NotFoundError
   from django.shortcuts import render

   @error_decorator
   def article_detail(request, article_id):
       try:
           article = Article.objects.get(id=article_id)
       except Article.DoesNotExist:
           raise NotFoundError("Article not found")

       return render(request, 'article.html', {'article': article})

In API Endpoints
~~~~~~~~~~~~~~~~

.. code-block:: python

   from apps.common.utilities.logger import ValidationError
   from rest_framework.decorators import api_view
   from rest_framework.response import Response

   @api_view(['POST'])
   def create_user(request):
       serializer = UserSerializer(data=request.data)

       if not serializer.is_valid():
           raise ValidationError(
               message="Invalid user data",
               field_errors=serializer.errors
           )

       user = serializer.save()
       return Response({'id': user.id}, status=201)

In Background Tasks
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from apps.common.utilities.logger import log_error, AppError
   import logging

   def process_batch_job(job_id):
       try:
           job = Job.objects.get(id=job_id)
           job.process()
       except Job.DoesNotExist:
           # Log but don't raise - background task
           error = AppError(f"Job {job_id} not found")
           log_error(error, level=logging.WARNING)
       except Exception as e:
           # Log critical errors
           log_error(e, level=logging.ERROR)
           # Optionally re-raise for task retry
           raise

Form Utilities
==============

The ``forms.py`` module provides utilities for form validation, error handling, and form enhancement with consistent patterns across the project.

FormValidationMixin
-------------------

Enhanced validation and error handling for Django forms.

**Features:**

- Standardized field validation
- Consistent error formatting
- Request context for validation
- Field requirement enforcement
- Custom validation hooks

**Usage Example:**

.. code-block:: python

   from django import forms
   from apps.common.utilities.forms import FormValidationMixin

   class UserRegistrationForm(FormValidationMixin, forms.Form):
       username = forms.CharField(max_length=100)
       email = forms.EmailField()
       password = forms.CharField(widget=forms.PasswordInput)
       confirm_password = forms.CharField(widget=forms.PasswordInput)

       # Define required fields
       required_fields = ['username', 'email', 'password']

       def __init__(self, *args, **kwargs):
           # Pass request context if available
           super().__init__(*args, **kwargs)

       def validate_form(self, cleaned_data):
           """Custom validation logic."""
           if cleaned_data.get('password') != cleaned_data.get('confirm_password'):
               self.add_error('confirm_password', 'Passwords do not match')

           # Check username availability
           if User.objects.filter(username=cleaned_data.get('username')).exists():
               self.add_error('username', 'Username already taken')

**In Views:**

.. code-block:: python

   def register_view(request):
       if request.method == 'POST':
           form = UserRegistrationForm(data=request.POST, request=request)

           if form.is_valid():
               # Form is valid
               user = create_user(form.cleaned_data)
               return redirect('profile', user_id=user.id)
           else:
               # Errors are automatically formatted
               errors = form.get_error_dict()
       else:
           form = UserRegistrationForm()

       return render(request, 'register.html', {'form': form})

BaseModelForm
-------------

Base model form with enhanced validation and error handling.

**Features:**

- Request context for model operations
- Pre/post save hooks
- Standardized validation
- Consistent error handling

**Usage Example:**

.. code-block:: python

   from django.forms import ModelForm
   from apps.common.utilities.forms import BaseModelForm
   from apps.users.models import UserProfile

   class UserProfileForm(BaseModelForm):
       class Meta:
           model = UserProfile
           fields = ['bio', 'location', 'website', 'avatar']

       def pre_save(self, instance, is_create):
           """Hook called before saving."""
           # Add custom logic before save
           instance.updated_by = self.request.user
           return instance

       def post_save(self, instance, is_create):
           """Hook called after saving."""
           # Add custom logic after save
           if is_create:
               send_welcome_email(instance.user)
           return instance

Form Helper Functions
---------------------

clean_form_data()
~~~~~~~~~~~~~~~~~

Clean form data for consistent processing.

.. code-block:: python

   from apps.common.utilities.forms import clean_form_data

   def clean_form_data(data: dict[str, Any]) -> dict[str, Any]:
       """Clean form data.

       - Converts empty strings to None
       - Strips whitespace from strings
       - Normalizes boolean values
       """

**Usage Example:**

.. code-block:: python

   from apps.common.utilities.forms import clean_form_data

   raw_data = {
       'name': '  John Doe  ',
       'email': '',
       'active': 'true',
       'age': '25'
   }

   cleaned = clean_form_data(raw_data)
   # {
   #     'name': 'John Doe',
   #     'email': None,
   #     'active': True,
   #     'age': '25'
   # }

validate_form_data()
~~~~~~~~~~~~~~~~~~~~

Validate form data using a Django form and return cleaned data or raise ValidationError.

.. code-block:: python

   from apps.common.utilities.forms import validate_form_data, ValidationError

   def api_create_user(request):
       try:
           # Validate using form class
           user, cleaned_data = validate_form_data(
               form_class=UserRegistrationForm,
               data=request.POST,
               request=request
           )

           return JsonResponse({'user_id': user.id})

       except ValidationError as e:
           return JsonResponse({
               'error': e.message,
               'field_errors': e.details.get('field_errors', {})
           }, status=400)

**For Model Forms:**

.. code-block:: python

   from apps.common.utilities.forms import validate_form_data

   # Update existing instance
   instance, cleaned_data = validate_form_data(
       form_class=UserProfileForm,
       data=request.POST,
       request=request,
       instance=user_profile
   )

HTMX Form Patterns
------------------

Using form utilities with HTMX for inline validation:

.. code-block:: python

   from apps.common.utilities.forms import FormValidationMixin
   from django.shortcuts import render

   def htmx_validate_field(request):
       """Validate a single field via HTMX."""
       form = UserRegistrationForm(data=request.POST)
       form.is_valid()  # Trigger validation

       field_name = request.POST.get('field_name')
       errors = form.errors.get(field_name, [])

       return render(request, 'partials/field_errors.html', {
           'field_name': field_name,
           'errors': errors
       })

Screenshot Service
==================

The ``screenshots.py`` module provides a service for capturing screenshots from the browser during development, testing, and debugging.

ScreenshotService Class
-----------------------

**Configuration Options:**

.. code-block:: python

   from apps.common.utilities.screenshots import ScreenshotService

   service = ScreenshotService(
       output_dir="screenshots",           # Directory to save screenshots
       server_url="http://localhost:8000", # Development server URL
       viewport={"width": 1280, "height": 800},  # Browser viewport
       headless=True,                      # Run browser in headless mode
       wait_before_capture=500,            # Wait time in milliseconds
   )

Basic Screenshot Capture
-------------------------

.. code-block:: python

   from apps.common.utilities.screenshots import ScreenshotService

   service = ScreenshotService()

   # Capture a simple screenshot
   output_path = service.capture(
       path="/accounts/profile/",
       filename="profile_page.png"
   )

Advanced Options
----------------

.. code-block:: python

   # Wait for specific element before capturing
   service.capture(
       path="/dashboard/",
       filename="dashboard_loaded.png",
       wait_for_selector="#dashboard-data",
       extra_wait_ms=1000
   )

   # Capture full page (not just viewport)
   service.capture(
       path="/docs/",
       filename="full_docs.png",
       full_page=True
   )

   # Capture authenticated pages
   cookies = [
       {
           'name': 'sessionid',
           'value': 'your_session_id',
           'domain': 'localhost',
           'path': '/'
       }
   ]

   service.capture(
       path="/private/dashboard/",
       filename="private_page.png",
       cookies=cookies
   )

Command-Line Interface
----------------------

Use the screenshot service from the command line:

.. code-block:: bash

   # Capture a simple screenshot
   python apps/common/utilities/screenshots.py /todos/

   # Use a specific filename
   python apps/common/utilities/screenshots.py /accounts/login/ \
       --filename login_screen.png

   # Wait for a specific element
   python apps/common/utilities/screenshots.py /accounts/profile/ \
       --wait-for "#profile-data"

   # Capture full page
   python apps/common/utilities/screenshots.py /docs/ --full-page

   # Show browser window during capture
   python apps/common/utilities/screenshots.py /dashboard/ --visible

Use Cases
---------

E2E Test Documentation
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from apps.common.utilities.screenshots import ScreenshotService

   def test_user_flow():
       service = ScreenshotService(output_dir="test_screenshots")

       # Document each step of the flow
       service.capture("/accounts/login/", "01_login_page.png")
       # ... perform login ...
       service.capture("/dashboard/", "02_dashboard.png")
       # ... perform actions ...
       service.capture("/profile/", "03_profile_updated.png")

Bug Reproduction
~~~~~~~~~~~~~~~~

.. code-block:: python

   # Capture the state when a bug occurs
   def handle_error(request):
       try:
           # Operation that might fail
           result = risky_operation()
       except Exception as e:
           # Capture screenshot for debugging
           service = ScreenshotService()
           service.capture(
               path=request.path,
               filename=f"bug_{e.__class__.__name__}_{timestamp}.png"
           )
           raise

Database Utilities
==================

The ``database/`` directory contains utilities for database operations and custom model fields.

Database Helpers
----------------

enum_to_choices()
~~~~~~~~~~~~~~~~~

Convert Python Enum to Django choices format.

.. code-block:: python

   from enum import Enum
   from apps.common.utilities.database.db import enum_to_choices

   class UserRole(Enum):
       ADMIN = 1
       MODERATOR = 2
       USER = 3

   # Convert to Django choices
   ROLE_CHOICES = enum_to_choices(UserRole)
   # [(1, 'ADMIN'), (2, 'MODERATOR'), (3, 'USER')]

   class User(models.Model):
       role = models.IntegerField(choices=ROLE_CHOICES)

Custom Model Fields
-------------------

MoneyField
~~~~~~~~~~

A custom field that stores currency as cents (integer) in the database but acts like a float in Python.

**Features:**

- Stores as integer (cents) in database for precision
- Presents as float in Python for easy calculation
- Handles conversion automatically

**Usage Example:**

.. code-block:: python

   from django.db import models
   from apps.common.utilities.database.model_fields import MoneyField

   class Product(models.Model):
       name = models.CharField(max_length=200)
       price = MoneyField(default=0)  # Stored as cents, used as dollars

       def apply_discount(self, percent):
           # Work with float values
           self.price = self.price * (1 - percent / 100)
           self.save()

   # Create a product
   product = Product.objects.create(
       name="Widget",
       price=29.99  # Stored as 2999 cents in DB
   )

   # Retrieve and use
   product = Product.objects.get(id=1)
   print(product.price)  # 29.99 (float)

   # Apply 10% discount
   product.apply_discount(10)
   print(product.price)  # 26.99

**Database Representation:**

- Python: ``29.99`` (float)
- Database: ``2999`` (integer, cents)

Processing Utilities
====================

The ``processing/`` directory contains utilities for data processing, text manipulation, and concurrent operations.

Multithreading
--------------

start_new_thread
~~~~~~~~~~~~~~~~

Decorator to run a function in a separate thread.

.. code-block:: python

   from apps.common.utilities.processing.multithreading import start_new_thread

   @start_new_thread
   def send_notification_email(user_id, message):
       """Send email in background thread."""
       user = User.objects.get(id=user_id)
       send_email(user.email, message)

       # Close DB connection when done
       from django.db import connection
       connection.close()

   # Usage - returns immediately, runs in background
   send_notification_email(user.id, "Welcome!")

**Important:** When running database transactions in threads, always close the connection:

.. code-block:: python

   @start_new_thread
   def background_task():
       # Your database operations
       User.objects.filter(active=True).update(last_checked=now())

       # Close connection at the end
       from django.db import connection
       connection.close()

run_all_multithreaded()
~~~~~~~~~~~~~~~~~~~~~~~~

Execute a function on multiple parameters concurrently using a thread pool.

.. code-block:: python

   from apps.common.utilities.processing.multithreading import run_all_multithreaded

   def process_user(user_id):
       user = User.objects.get(id=user_id)
       # Process user...
       return user.username

   # Process 100 users in parallel (16 threads)
   user_ids = list(range(1, 101))
   results = run_all_multithreaded(process_user, user_ids)

**With Multiple Parameters:**

.. code-block:: python

   def update_profile(params):
       user_id, new_bio = params
       profile = UserProfile.objects.get(user_id=user_id)
       profile.bio = new_bio
       profile.save()

   # List of tuples for multiple parameters
   params_list = [
       (1, "New bio for user 1"),
       (2, "New bio for user 2"),
       (3, "New bio for user 3"),
   ]

   results = run_all_multithreaded(update_profile, params_list)

Regex Utilities
---------------

extractEmail()
~~~~~~~~~~~~~~

Extract email addresses from text using regex.

.. code-block:: python

   from apps.common.utilities.processing.regex import extractEmail

   text = """
   Contact us at support@example.com or sales@example.com
   You can also reach john.doe@company.org
   """

   # Get all emails
   emails = extractEmail(text, return_all=True)
   # ['support@example.com', 'sales@example.com', 'john.doe@company.org']

   # Get first email only
   first_email = extractEmail(text, return_all=False)
   # 'support@example.com'

**Supported Formats:**

- Standard: ``user@example.com``
- With dots: ``john.doe@example.com``
- With special chars: ``user+tag@example.com``
- Obfuscated: ``user at example dot com`` (converted automatically)

Unicode Tools
-------------

clean_text()
~~~~~~~~~~~~

Remove all control characters from text, including line feeds and carriage returns.

.. code-block:: python

   from apps.common.utilities.processing.unicode_tools import clean_text

   text = "Hello\x00World\r\nTest\x1b"
   cleaned = clean_text(text)
   # "HelloWorldTest"

remove_control_chars()
~~~~~~~~~~~~~~~~~~~~~~

Remove control characters while preserving other content.

.. code-block:: python

   from apps.common.utilities.processing.unicode_tools import remove_control_chars

   text = "Normal text\x00with\x01control\x02chars"
   cleaned = remove_control_chars(text)
   # "Normal textwithcontrolchars"

remove_html_tags()
~~~~~~~~~~~~~~~~~~

Remove HTML tags from text (preserving ``<img>`` tags).

.. code-block:: python

   from apps.common.utilities.processing.unicode_tools import remove_html_tags

   html = "<p>This is <strong>bold</strong> text with <img src='photo.jpg'> image</p>"
   text = remove_html_tags(html)
   # "This is bold text with <img src='photo.jpg'> image"

**Use Cases:**

- Sanitizing user input
- Converting HTML to plain text
- Preserving images while removing formatting

Serializers
-----------

TimeZoneField
~~~~~~~~~~~~~

Custom DRF serializer field for timezone fields.

.. code-block:: python

   from rest_framework import serializers
   from apps.common.utilities.processing.serializers import TimeZoneField

   class UserProfileSerializer(serializers.ModelSerializer):
       timezone = TimeZoneField(required=False, allow_null=True)

       class Meta:
           model = UserProfile
           fields = ['id', 'timezone', 'language']

WritableSerializerMethodField
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A SerializerMethodField that supports write operations.

.. code-block:: python

   from rest_framework import serializers
   from apps.common.utilities.processing.serializers import WritableSerializerMethodField

   class UserSerializer(serializers.ModelSerializer):
       full_name = WritableSerializerMethodField(
           deserializer_field=serializers.CharField()
       )

       def get_full_name(self, obj):
           return f"{obj.first_name} {obj.last_name}"

       def set_full_name(self, value):
           # Split and set first/last name
           parts = value.split(' ', 1)
           self.instance.first_name = parts[0]
           self.instance.last_name = parts[1] if len(parts) > 1 else ''

English Language
----------------

build_english_list()
~~~~~~~~~~~~~~~~~~~~

Build a grammatically correct English list from items.

.. code-block:: python

   from apps.common.utilities.processing.english_language import build_english_list

   # Two items
   items = ['apples', 'oranges']
   result = build_english_list(items)
   # "apples and oranges"

   # Three or more items
   items = ['apples', 'oranges', 'bananas']
   result = build_english_list(items)
   # "apples, oranges, and bananas"

   # Single item
   items = ['apples']
   result = build_english_list(items)
   # "apples"

   # Empty list
   items = []
   result = build_english_list(items)
   # ""

**Usage Example:**

.. code-block:: python

   def format_notification(users):
       names = [user.first_name for user in users]
       user_list = build_english_list(names)
       return f"{user_list} commented on your post"

   # Output examples:
   # "Alice commented on your post"
   # "Alice and Bob commented on your post"
   # "Alice, Bob, and Charlie commented on your post"

cap_first_word()
~~~~~~~~~~~~~~~~

Capitalize the first word of a string or list.

.. code-block:: python

   from apps.common.utilities.processing.english_language import cap_first_word

   # String input
   text = "hello world"
   result = cap_first_word(text)
   # "Hello world"

   # List input
   words = ['hello', 'world']
   result = cap_first_word(words)
   # ['Hello', 'world']

ends_with_period()
~~~~~~~~~~~~~~~~~~

Check if a string ends with a period.

.. code-block:: python

   from apps.common.utilities.processing.english_language import ends_with_period

   ends_with_period("Hello world.")  # True
   ends_with_period("Hello world")   # False

Django Utilities
================

The ``django/`` directory contains Django-specific utilities including custom backends and middleware.

Authentication Backends
-----------------------

EmailAuthBackend
~~~~~~~~~~~~~~~~

Allow users to authenticate with email address instead of username.

**Configuration in settings.py:**

.. code-block:: python

   AUTHENTICATION_BACKENDS = [
       'apps.common.utilities.django.backends.EmailAuthBackend',
       'django.contrib.auth.backends.ModelBackend',  # Fallback to username
   ]

**Usage:**

.. code-block:: python

   from django.contrib.auth import authenticate, login

   def login_view(request):
       if request.method == 'POST':
           email = request.POST['email']
           password = request.POST['password']

           # Authenticate with email
           user = authenticate(request, username=email, password=password)

           if user is not None:
               login(request, user)
               return redirect('dashboard')
           else:
               return render(request, 'login.html', {
                   'error': 'Invalid email or password'
               })

       return render(request, 'login.html')

Middleware
----------

APIHeaderMiddleware
~~~~~~~~~~~~~~~~~~~

Add custom headers to API responses.

**Configuration in settings.py:**

.. code-block:: python

   MIDDLEWARE = [
       # ... other middleware
       'apps.common.utilities.django.middleware.APIHeaderMiddleware',
   ]

**Features:**

- Adds ``X-Required-Main-Build`` header to all responses
- Useful for version tracking and client compatibility
- Reads from environment variable

**Environment Configuration:**

.. code-block:: bash

   # .env
   Required-Main-Build=1.2.3

DRF Permissions
===============

The ``drf_permissions/`` directory contains custom permission classes for Django REST Framework.

API Key Permissions
-------------------

HasUserAPIKey
~~~~~~~~~~~~~

Permission class for user-based API key authentication.

.. code-block:: python

   from rest_framework.decorators import api_view, permission_classes
   from apps.common.utilities.drf_permissions.api_key import HasUserAPIKey

   @api_view(['GET'])
   @permission_classes([HasUserAPIKey])
   def user_profile(request):
       # request.user is automatically set from API key
       # request.api_key contains the API key object
       return Response({
           'id': request.user.id,
           'username': request.user.username,
           'api_key_name': request.api_key.name
       })

**Class-Based Views:**

.. code-block:: python

   from rest_framework.views import APIView
   from apps.common.utilities.drf_permissions.api_key import HasUserAPIKey

   class UserDataView(APIView):
       permission_classes = [HasUserAPIKey]

       def get(self, request):
           # User is authenticated via API key
           return Response({
               'user': request.user.username,
               'data': get_user_data(request.user)
           })

HasTeamAPIKey
~~~~~~~~~~~~~

Permission class for team-based API key authentication.

.. code-block:: python

   from rest_framework.decorators import api_view, permission_classes
   from apps.common.utilities.drf_permissions.api_key import HasTeamAPIKey

   @api_view(['GET'])
   @permission_classes([HasTeamAPIKey])
   def team_data(request):
       # request.team is automatically set from API key
       # request.api_key contains the API key object
       return Response({
           'team': request.team.name,
           'members': request.team.members.count(),
           'api_key_name': request.api_key.name
       })

HasAnyAPIKey
~~~~~~~~~~~~

Permission class that accepts either user or team API keys.

.. code-block:: python

   from rest_framework.decorators import api_view, permission_classes
   from apps.common.utilities.drf_permissions.api_key import HasAnyAPIKey

   @api_view(['GET'])
   @permission_classes([HasAnyAPIKey])
   def shared_resource(request):
       # Check which type of authentication was used
       if hasattr(request, 'user') and request.user.is_authenticated:
           return Response({'type': 'user', 'name': request.user.username})
       elif hasattr(request, 'team'):
           return Response({'type': 'team', 'name': request.team.name})

**Usage Notes:**

- API keys must be included in the ``Authorization`` header
- Format: ``Authorization: Api-Key YOUR_API_KEY``
- Keys are automatically validated and attached to the request

Compression Utilities
=====================

The ``compression/`` directory contains utilities for image compression and optimization.

Image Compression
-----------------

zoom_and_crop()
~~~~~~~~~~~~~~~

Zoom, crop, and resize images with advanced positioning options.

.. code-block:: python

   from PIL import Image
   from apps.common.utilities.compression.image_compression import zoom_and_crop

   # Open an image
   image = Image.open('photo.jpg')

   # Basic crop and resize
   result = zoom_and_crop(
       image=image,
       resize_dimensions=(300, 300)
   )

   # Zoom in (0 = no zoom, 1 = maximum zoom)
   result = zoom_and_crop(
       image=image,
       zoom=0.5,
       resize_dimensions=(300, 300)
   )

   # Crop from off-center position
   import numpy as np
   result = zoom_and_crop(
       image=image,
       zoom=0.3,
       angle_from_center=np.pi / 4,  # 45 degrees
       distance_from_center=0.3,     # 30% from center
       resize_dimensions=(300, 300)
   )

**Parameters:**

- ``image``: PIL Image object
- ``zoom``: Zoom level (0-1, where 0 is no zoom, 1 is maximum)
- ``angle_from_center``: Angle in radians for off-center cropping
- ``distance_from_center``: Distance from center (0-1)
- ``is_orig_image_landscape``: Whether the original image is landscape
- ``resize_dimensions``: Target dimensions (width, height)

**Use Cases:**

- Creating profile picture thumbnails
- Generating different image sizes for responsive design
- Smart cropping for featured images
- Image preprocessing for machine learning

**Example Pipeline:**

.. code-block:: python

   from PIL import Image
   from apps.common.utilities.compression.image_compression import zoom_and_crop

   def create_thumbnails(image_path):
       image = Image.open(image_path)

       # Create different thumbnail sizes
       sizes = [
           (150, 150),  # Small
           (300, 300),  # Medium
           (600, 600),  # Large
       ]

       thumbnails = []
       for size in sizes:
           thumb = zoom_and_crop(
               image=image,
               zoom=0.2,  # Slight zoom
               resize_dimensions=size
           )
           thumbnails.append(thumb)

       return thumbnails

Email Utilities
===============

The ``email.py`` module provides utilities for working with email messages.

email_to_string()
-----------------

Convert an EmailMessage object to a readable string format.

.. code-block:: python

   from django.core.mail import EmailMessage
   from apps.common.utilities.email import email_to_string

   # Create an email
   email = EmailMessage(
       subject='Welcome to our platform',
       body='Thank you for signing up!',
       from_email='noreply@example.com',
       to=['user@example.com'],
       cc=['admin@example.com'],
       reply_to=['support@example.com']
   )

   # Convert to string for logging or debugging
   email_string = email_to_string(email)
   print(email_string)

**Output Format:**

.. code-block:: text

   From: noreply@example.com
   To: ['user@example.com']
   Subject: Welcome to our platform
   Reply-To: ['support@example.com']
   CC: ['admin@example.com']
   BCC: Not specified
   Body: Thank you for signing up!
   Attachments: []

**Use Cases:**

- Logging sent emails
- Debugging email configurations
- Email audit trails
- Testing email content

Best Practices
==============

Error Handling
--------------

1. **Use Specific Exceptions**: Choose the most specific exception type

   .. code-block:: python

      # Good
      raise NotFoundError("User not found")

      # Avoid
      raise AppError("User not found", status_code=404)

2. **Include Context**: Add helpful details to exceptions

   .. code-block:: python

      raise ValidationError(
          message="Invalid order",
          field_errors={
              'quantity': ['Must be greater than 0'],
              'product_id': ['Product does not exist']
          }
      )

3. **Log Appropriately**: Choose the right log level

   .. code-block:: python

      # User errors - WARNING
      log_error(validation_error, request, level=logging.WARNING)

      # System errors - ERROR
      log_error(database_error, request, level=logging.ERROR)

4. **Use Decorators for Views**: Simplify error handling

   .. code-block:: python

      @error_decorator
      def my_view(request):
          # Automatic error handling
          pass

Form Validation
---------------

1. **Use Mixins**: Leverage FormValidationMixin for consistency

2. **Request Context**: Pass request when available

   .. code-block:: python

      form = MyForm(data=request.POST, request=request)

3. **Custom Validation**: Use ``validate_form()`` method

4. **Error Format**: Use ``get_error_dict()`` for standardized errors

Multithreading
--------------

1. **Close Connections**: Always close database connections in threads

   .. code-block:: python

      @start_new_thread
      def background_task():
          # Your code
          from django.db import connection
          connection.close()

2. **Thread Pool Size**: Default is 16, adjust based on workload

3. **Error Handling**: Include try/except in threaded functions

4. **Avoid UI Operations**: Don't manipulate request/response in threads

Adding New Utilities
====================

When adding new utilities to the collection, follow these guidelines:

Location
--------

- **General utilities**: Root of ``utilities/`` directory
- **Category-specific**: Create or use existing subdirectories
- **Django-specific**: ``django/`` subdirectory
- **DRF-specific**: ``drf_permissions/`` subdirectory
- **Processing**: ``processing/`` subdirectory

Documentation
-------------

1. **Docstrings**: Include comprehensive docstrings

   .. code-block:: python

      def my_utility(param1: str, param2: int = 0) -> str:
          """Short description.

          Longer description explaining the purpose and behavior.

          Args:
              param1: Description of param1
              param2: Description of param2 (default: 0)

          Returns:
              Description of return value

          Raises:
              ValidationError: When validation fails

          Example:
              >>> result = my_utility("test", 5)
              >>> print(result)
              "test-5"
          """

2. **Type Hints**: Use type hints for all parameters and returns

3. **Examples**: Provide usage examples in docstrings

Testing
-------

1. **Unit Tests**: Write tests for each utility function

   .. code-block:: python

      # apps/common/tests/test_utilities.py
      from apps.common.utilities.my_module import my_function

      def test_my_function():
          result = my_function("input")
          assert result == "expected output"

2. **Edge Cases**: Test boundary conditions and error cases

3. **Integration Tests**: Test utilities in realistic scenarios

Import Structure
----------------

Make utilities easily importable:

.. code-block:: python

   # In __init__.py of subdirectories
   from .my_module import my_function, MyClass

   __all__ = ['my_function', 'MyClass']

Code Style
----------

1. Follow PEP 8 style guidelines
2. Use descriptive names
3. Keep functions focused and small
4. Add comments for complex logic
5. Use modern Python features (type hints, f-strings, etc.)

Common Patterns
===============

Validation Pattern
------------------

.. code-block:: python

   from apps.common.utilities.logger import ValidationError

   def validate_and_process(data):
       # Validate input
       errors = {}

       if not data.get('email'):
           errors['email'] = ['Email is required']

       if not data.get('age') or data['age'] < 18:
           errors['age'] = ['Must be 18 or older']

       if errors:
           raise ValidationError(
               message="Invalid data",
               field_errors=errors
           )

       # Process valid data
       return process_data(data)

Safe Resource Access
--------------------

.. code-block:: python

   from apps.common.utilities.logger import NotFoundError

   def get_user_resource(user_id, resource_id):
       try:
           user = User.objects.get(id=user_id)
       except User.DoesNotExist:
           raise NotFoundError("User not found")

       try:
           resource = Resource.objects.get(id=resource_id, owner=user)
       except Resource.DoesNotExist:
           raise NotFoundError("Resource not found or not accessible")

       return resource

Background Processing
---------------------

.. code-block:: python

   from apps.common.utilities.processing.multithreading import start_new_thread
   from apps.common.utilities.logger import log_error

   @start_new_thread
   def process_in_background(item_id):
       try:
           item = Item.objects.get(id=item_id)
           item.process()
       except Exception as e:
           log_error(e)
       finally:
           from django.db import connection
           connection.close()

API Response Pattern
--------------------

.. code-block:: python

   from apps.common.utilities.logger import ValidationError, NotFoundError
   from rest_framework.decorators import api_view
   from rest_framework.response import Response

   @api_view(['POST'])
   def api_endpoint(request):
       # Validation
       if not request.data.get('required_field'):
           raise ValidationError(
               message="Missing required field",
               field_errors={'required_field': ['This field is required']}
           )

       # Resource access
       try:
           resource = Resource.objects.get(id=request.data['resource_id'])
       except Resource.DoesNotExist:
           raise NotFoundError("Resource not found")

       # Processing
       result = process_resource(resource, request.data)

       return Response({'result': result}, status=200)

Troubleshooting
===============

Common Issues
-------------

Import Errors
~~~~~~~~~~~~~

**Problem**: Cannot import utility module

**Solution**: Ensure you're using the correct import path:

.. code-block:: python

   # Correct
   from apps.common.utilities.logger import AppError

   # Incorrect
   from common.utilities.logger import AppError

Thread Database Errors
~~~~~~~~~~~~~~~~~~~~~~

**Problem**: Database connection errors in threaded functions

**Solution**: Always close the connection:

.. code-block:: python

   @start_new_thread
   def my_function():
       # Your code here
       from django.db import connection
       connection.close()

Form Validation Not Working
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Problem**: Custom validation not being called

**Solution**: Ensure you're calling ``is_valid()``:

.. code-block:: python

   form = MyForm(data=request.POST)
   if form.is_valid():  # This triggers validation
       # Process form

API Key Authentication Failing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Problem**: API key not recognized

**Solution**: Check the header format:

.. code-block:: bash

   # Correct
   Authorization: Api-Key YOUR_KEY_HERE

   # Incorrect
   Authorization: Bearer YOUR_KEY_HERE
   Authorization: ApiKey YOUR_KEY_HERE

Screenshot Service Not Working
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Problem**: Screenshots not being captured

**Solution**: Ensure Playwright is installed:

.. code-block:: bash

   uv add --dev playwright
   python -m playwright install chromium

Related Documentation
=====================

- :doc:`/development/error_handling` - Detailed error handling guide
- :doc:`/api/index` - API endpoint documentation
- :doc:`/models/index` - Model documentation
- :doc:`/views/index` - View documentation

Further Reading
---------------

- `Django Forms Documentation <https://docs.djangoproject.com/en/stable/topics/forms/>`_
- `Django REST Framework Permissions <https://www.django-rest-framework.org/api-guide/permissions/>`_
- `Python Threading <https://docs.python.org/3/library/threading.html>`_
- `Playwright Documentation <https://playwright.dev/python/>`_
