# TODO List for Django Project Template

## Completed Tasks ✅
- ✅ Added comprehensive behavior mixin examples with BlogPost model
- ✅ Created detailed setup guide for new developers
- ✅ Implemented Loops email integration with tests
- ✅ Improved test coverage for models and behaviors
- ✅ Upgraded admin interface with Django Unfold and Tailwind
- ✅ Implemented Team models with permissions system
- ✅ Removed component framework dependencies
- ✅ Upgraded to uv for dependency management

## Current Priority Tasks

### 1. Template and Static File Organization
- [x] Audit all app-level template directories and create migration plan
- [x] Move templates from apps/public/templates to root templates directory
- [x] Update template references in views and URL configurations
- [x] Consolidate static files from apps/public/static to root static directory
- [x] Update static file references in templates
- [x] Remove "dont_put_things_here.txt" from static directory
- [ ] Reorganize templates for better HTMX integration
  - [ ] Create dedicated partial template directory structure
  - [ ] Implement standardized naming convention for partials
  - [ ] Add template documentation in comments
- [ ] Document HTMX integration patterns with examples
- [ ] Update documentation on template patterns

### 2. Extend Test Coverage
- [ ] Add API endpoint tests with APITestCase
- [ ] Add view tests with proper request mocking
- [ ] Create comprehensive test fixtures for all models

### 3. Dependency Management Improvements
- [ ] Create pyproject.toml with project metadata
- [ ] Update build.sh script to use uv for dependency installation
- [ ] Setup pre-commit hooks for code quality (black, isort, flake8, mypy)

### 4. User Experience Improvements
- [ ] Implement basic Team-related views (create, join, manage)
- [ ] Add user authentication templates (reset password, etc.)
- [ ] Create reusable form components
- [ ] Modernize base templates with best practices

### 5. App Restructuring
- [ ] Create new apps/ai/ directory structure 
- [ ] Set up apps/ai/__init__.py, apps.py, models, views, and urls
- [ ] Create initial models for AI agent workflows
- [ ] Add apps.ai to INSTALLED_APPS
- [ ] Audit apps/communication for models and functionality to merge
- [ ] Migrate communication models to apps/common
- [ ] Remove apps/communication after successful migration

## Documentation Tasks
- [ ] Document HTMX integration patterns with examples
- [ ] Add API documentation with OpenAPI/Swagger
- [ ] Create architecture diagram showing app relationships

## Infrastructure Tasks
- [ ] Dockerize the application with proper configuration
  - [ ] Update Dockerfile for production use
  - [ ] Create docker-compose.yml for local development
  - [ ] Add Docker documentation and examples
  - [ ] Implement multi-stage builds for efficiency
- [ ] Standardize environment variable and secrets management
  - [ ] Replace settings/local.py with .env file approach
  - [ ] Update documentation for environment setup
  - [ ] Create .env.example with all required variables
  - [ ] Update settings to load from environment variables
- [ ] Add GitHub Actions workflow for testing
- [ ] Create deployment pipeline for staging/production
- [ ] Setup monitoring and error tracking

## Code Quality Tasks
- [ ] Implement consistent error handling strategy
- [ ] Refactor redundant template logic
- [ ] Update to latest Django version
- [ ] Standardize form validation approach
- [ ] Improve type annotations across codebase

## Frontend Tasks
- [ ] Implement design system components
- [ ] Add JavaScript bundling with Webpack/Vite
- [ ] Create unified CSS approach (Tailwind only)
- [ ] Implement responsive layouts
- [ ] Add dark mode support
- [ ] Add internationalization support
- [ ] Integrate payment processing example