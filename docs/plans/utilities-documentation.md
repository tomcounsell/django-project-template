# Documentation Plan: Common Utilities Collection

## Overview

The `apps/common/utilities/` directory contains a rich collection of helper functions, classes, and utilities that solve common problems in Django development. These go well beyond Django's built-in utilities, providing production-ready solutions for logging, forms, screenshots, text processing, and more.

## Target Audience

- All developers working in the codebase
- Teams looking for pre-built solutions to common problems
- Developers standardizing patterns across projects

## Documentation Structure

### 1. Utilities Overview (1 page) ✅
- **Purpose** - Why centralized utilities exist ✅
- **Organization** - How utilities are categorized ✅
- **Import Conventions** - How to import and use ✅
- **Adding New Utilities** - Guidelines for contributions ✅

### 2. Logger & Error Handling (`logger.py`) (2 pages) ✅

#### 2.1 Exception Classes ✅
- **AppError** - Base exception with message, code, status_code, details ✅
- **ValidationError** - Data validation errors with field-level details ✅
- **AuthenticationError** - Auth failures ✅
- **PermissionError** - Authorization failures ✅
- **NotFoundError** - Resource not found ✅
- **ConflictError** - Resource conflicts (documented) ✅

#### 2.2 Logging Functions ✅
- **log_error()** - Standard error logging with context ✅
- **Structured logging** - Adding context to logs ✅

#### 2.3 Error Handling Decorators ✅
- **@error_decorator** - Automatic exception handling for views ✅
- **ErrorHandlingMixin** - Class-based view error handling ✅
- **@raises_app_error** - Transform exceptions to AppError ✅

#### 2.4 Response Helpers ✅
- **handle_view_exception()** - Standardized error responses ✅
- **api_exception_handler()** - DRF exception handler ✅
- **API vs. HTML responses** - Automatic format detection ✅

#### 2.5 Integration ✅
- How to use in views ✅
- How to use in API endpoints ✅
- How to use in background tasks ✅

### 3. Form Utilities (`forms.py`) (1 page) ✅

#### 3.1 FormValidationMixin ✅
- **Purpose** - Enhanced validation for Django forms ✅
- **Features**: ✅
  - Standardized field validation ✅
  - Consistent error formatting ✅
  - Request context for validation ✅
  - Field requirement enforcement ✅
- **Usage Example** - Complete form with mixin ✅

#### 3.2 Form Helpers ✅
- **clean_form_data()** - Clean form data for processing ✅
- **validate_form_data()** - Validate using form class ✅
- **BaseModelForm** - Enhanced model form ✅

#### 3.3 HTMX Form Patterns ✅
- Form validation with HTMX ✅
- Inline error display ✅

### 4. Screenshot Service (`screenshots.py`) (1 page) ✅

#### 4.1 Overview ✅
- **Purpose** - Capture UI states for debugging, testing, documentation ✅
- **Backends**: ✅
  - Playwright (primary) ✅
  - Browser-use (AI-powered) ✅

#### 4.2 ScreenshotService Class ✅
- **Configuration** - output_dir, viewport, headless mode ✅
- **Methods**: ✅
  - `capture(url, filename)` - Single screenshot ✅
  - `capture_with_auth(url, credentials)` - Authenticated pages ✅
  - `capture_with_browser_agent()` - AI-powered capture ✅
- **Output Management** - Naming, directories ✅

#### 4.3 Use Cases ✅
- E2E test documentation ✅
- Bug reproduction ✅
- Command-line interface ✅

### 5. Database Utilities (`database/`) (1 page) ✅

#### 5.1 db.py ✅
- **enum_to_choices()** - Convert Python Enum to Django choices ✅

#### 5.2 model_fields.py ✅
- **MoneyField** - Currency field stored as cents ✅
- Field validators ✅
- Field utilities ✅

### 6. Processing Utilities (`processing/`) (1 page) ✅

#### 6.1 Multithreading (`multithreading.py`) ✅
- **@start_new_thread** - Decorator for background threads ✅
- **run_all_multithreaded()** - Thread pool utilities ✅
- **Database connection handling** - Best practices ✅

#### 6.2 Regex (`regex.py`) ✅
- **extractEmail()** - Extract email addresses from text ✅
- **Common patterns** - Email extraction with obfuscation support ✅

#### 6.3 Unicode Tools (`unicode_tools.py`) ✅
- **clean_text()** - Remove control characters ✅
- **remove_control_chars()** - Character handling ✅
- **remove_html_tags()** - HTML tag removal ✅

#### 6.4 Serializers (`serializers.py`) ✅
- **TimeZoneField** - Custom timezone serializer field ✅
- **WritableSerializerMethodField** - Writable method field ✅

#### 6.5 English Language (`english_language.py`) ✅
- **build_english_list()** - Grammatically correct lists ✅
- **cap_first_word()** - Capitalize first word ✅
- **ends_with_period()** - Check for period ending ✅

### 7. Django Utilities (`django/`) (1 page) ✅

#### 7.1 Backends (`backends.py`) ✅
- **EmailAuthBackend** - Email-based authentication ✅

#### 7.2 Middleware (`middleware.py`) ✅
- **APIHeaderMiddleware** - Custom API headers ✅

### 8. DRF Permissions (`drf_permissions/`) (1 page) ✅

#### 8.1 API Key Permissions ✅
- **HasUserAPIKey** - User API key authentication ✅
- **HasTeamAPIKey** - Team API key authentication ✅
- **HasAnyAPIKey** - Accept any valid API key ✅

### 9. Compression (`compression/`) (0.5 page) ✅

#### 9.1 Image Compression ✅
- **zoom_and_crop()** - Image zoom, crop, and resize ✅
- **Smart cropping** - Off-center positioning ✅
- **Use cases** - Thumbnails, responsive images ✅

### 10. Email Utilities (`email.py`) (0.5 page) ✅
- **email_to_string()** - Convert EmailMessage to string ✅
- **Usage** - Logging and debugging ✅

## Content Sources

- Source files: `apps/common/utilities/`
- Existing docs: `docs/ERROR_HANDLING.md`
- Tests: `apps/common/tests/test_error_handling.py`

## Implementation Notes

### Sphinx Integration
- Autodoc all utility modules
- Include all public functions and classes
- Group by subdirectory

### Code Examples
- Each utility should have at least one real-world example
- Show common use cases
- Include error handling

### Cross-References
- Link to views that use these utilities
- Link to tests for usage examples
- Link to related Django docs

## Estimated Effort

- Writing: 5-6 hours
- Code examples: 2 hours
- Sphinx integration: 1-2 hours
- Review & polish: 1 hour

**Total: 9-11 hours**

## Success Criteria

1. Developers can find the right utility for their problem within 2 minutes
2. All public functions have docstrings and examples
3. Error handling patterns are clear and consistent
4. Import paths are documented clearly
5. Common patterns from existing code are documented
