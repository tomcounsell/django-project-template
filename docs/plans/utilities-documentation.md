# Documentation Plan: Common Utilities Collection

## Overview

The `apps/common/utilities/` directory contains a rich collection of helper functions, classes, and utilities that solve common problems in Django development. These go well beyond Django's built-in utilities, providing production-ready solutions for logging, forms, screenshots, text processing, and more.

## Target Audience

- All developers working in the codebase
- Teams looking for pre-built solutions to common problems
- Developers standardizing patterns across projects

## Documentation Structure

### 1. Utilities Overview (1 page)
- **Purpose** - Why centralized utilities exist
- **Organization** - How utilities are categorized
- **Import Conventions** - How to import and use
- **Adding New Utilities** - Guidelines for contributions

### 2. Logger & Error Handling (`logger.py`) (2 pages)

#### 2.1 Exception Classes
- **AppError** - Base exception with message, code, status_code, details
- **ValidationError** - Data validation errors with field-level details
- **AuthenticationError** - Auth failures
- **PermissionError** - Authorization failures
- **NotFoundError** - Resource not found
- **RateLimitError** - Rate limit exceeded

#### 2.2 Logging Functions
- **log_error()** - Standard error logging with context
- **log_info()** - Information logging
- **log_warning()** - Warning logging
- **log_debug()** - Debug logging
- **Structured logging** - Adding context to logs

#### 2.3 Error Handling Decorators
- **@handle_exceptions** - Automatic exception handling for views
- **@api_error_handler** - DRF-specific error handling
- **@log_function_call** - Log function entry/exit

#### 2.4 Response Helpers
- **error_response()** - Standardized error responses
- **success_response()** - Standardized success responses
- **API vs. HTML responses** - Automatic format detection

#### 2.5 Integration
- How to use in views
- How to use in API endpoints
- How to use in background tasks
- Sentry/error tracking integration

### 3. Form Utilities (`forms.py`) (1 page)

#### 3.1 FormValidationMixin
- **Purpose** - Enhanced validation for Django forms
- **Features**:
  - Standardized field validation
  - Consistent error formatting
  - Request context for validation
  - Field requirement enforcement
- **Usage Example** - Complete form with mixin

#### 3.2 Form Helpers
- **clean_phone_number()** - Phone number normalization
- **clean_email()** - Email normalization
- **validate_password_strength()** - Password validation
- Other field-specific cleaners

#### 3.3 HTMX Form Patterns
- Form validation with HTMX
- Inline error display
- Success handling

### 4. Screenshot Service (`screenshots.py`) (1 page)

#### 4.1 Overview
- **Purpose** - Capture UI states for debugging, testing, documentation
- **Backends**:
  - Playwright (primary)
  - Browser-use (AI-powered)

#### 4.2 ScreenshotService Class
- **Configuration** - output_dir, viewport, headless mode
- **Methods**:
  - `capture(url, filename)` - Single screenshot
  - `capture_sequence(urls)` - Multiple screenshots
  - `capture_with_auth(url, credentials)` - Authenticated pages
- **Output Management** - Naming, directories, cleanup

#### 4.3 Use Cases
- E2E test documentation
- Bug reproduction
- Visual regression testing
- Documentation generation

### 5. Database Utilities (`database/`) (1 page)

#### 5.1 db.py
- Database connection helpers
- Query utilities
- Transaction management helpers

#### 5.2 model_fields.py
- Custom model field types
- Field validators
- Field utilities

### 6. Processing Utilities (`processing/`) (1 page)

#### 6.1 Multithreading (`multithreading.py`)
- **Thread pool utilities** - Parallel processing helpers
- **Async helpers** - Working with Django async
- **Rate limiting** - Controlling concurrent operations

#### 6.2 Regex (`regex.py`)
- **Common patterns** - Pre-compiled regex for common use cases
- **Pattern helpers** - Building and testing regex

#### 6.3 Unicode Tools (`unicode_tools.py`)
- **Normalization** - Unicode normalization utilities
- **Character handling** - Special character processing
- **Encoding helpers** - UTF-8 handling

#### 6.4 Serializers (`serializers.py`)
- **Custom serializers** - Beyond DRF defaults
- **Serialization helpers** - Common patterns

#### 6.5 English Language (`english_language.py`)
- **Text processing** - Common English text operations
- **Pluralization** - Correct plural forms
- **Formatting** - Human-readable text formatting

### 7. Django Utilities (`django/`) (1 page)

#### 7.1 Backends (`backends.py`)
- Custom authentication backends
- Custom storage backends
- Custom middleware helpers

#### 7.2 Other Django Helpers
- Settings utilities
- URL utilities
- Template helpers

### 8. DRF Permissions (`drf_permissions/`) (1 page)

#### 8.1 API Key Permissions
- **HasAPIKey** - API key authentication
- **Key management** - Creating, revoking keys
- **Rate limiting** - Per-key rate limits

#### 8.2 Custom Permission Classes
- Team-based permissions
- Object-level permissions
- Compound permissions

### 9. Compression (`compression/`) (0.5 page)

#### 9.1 Image Compression
- **image_compression.py** - Image optimization
- **Supported formats** - JPEG, PNG, WebP
- **Quality settings** - Compression vs. quality tradeoffs
- **Usage** - Before upload, on-demand

### 10. Email Utilities (`email.py`) (0.5 page)
- **Email helpers** - Common email operations
- **Template rendering** - HTML email generation
- **Testing emails** - Development environment

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
