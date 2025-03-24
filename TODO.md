# TODO List for Django Project Template

## High Priority Tasks (Implementation Order)

### 1. Test Coverage Improvement (100% goal)
- [x] Create test factory classes for common models
- [x] Set up coverage tools (pytest-cov) and reporting
- [x] Add coverage check to CI pipeline with target thresholds
- [x] Create test mixins for common test patterns
- [x] Complete behavior mixin tests:
  - [x] Audit existing tests for Timestampable, Authorable behaviors
  - [x] Implement missing tests for Publishable behavior
  - [x] Implement missing tests for Expirable behavior
  - [x] Implement missing tests for Locatable behavior
  - [x] Implement missing tests for Permalinkable behavior
  - [x] Implement missing tests for Annotatable behavior
  - [x] Create standalone behavior tests that run without Django setup
- [ ] Complete model tests:
  - [x] Audit existing model tests (Address, Country, Currency, Note, Upload)
  - [x] Add tests for User model
  - [x] Add tests for Image model
  - [x] Add tests for Document model
  - [x] Add tests for Background Job model
  - [x] Add tests for City model
- [ ] Add API endpoint tests with APITestCase
- [ ] Add view tests with proper request mocking
- [ ] Create comprehensive test fixtures for all models
- [ ] Write complete test suite for Loops email integration:
  - [ ] Mock Loops API responses for unit tests
  - [ ] Test LoopsClient class with all endpoints
  - [ ] Test error handling and API errors
  - [ ] Test all transactional email shortcuts
  - [ ] Create fixtures for common email templates

### 2. Template and Static File Consolidation
- [ ] Audit all app-level template directories and create migration plan
- [ ] Move templates from apps/public/templates to root templates directory
- [ ] Update template references in views and URL configurations
- [ ] Consolidate static files from apps/public/static to root static directory
- [ ] Update static file references in templates
- [ ] Remove "dont_put_things_here.txt" from static directory
- [ ] Reorganize templates for better HTMX integration
  - [ ] Create dedicated partial template directory structure
  - [ ] Implement standardized naming convention for partials
  - [ ] Add template documentation in comments

### 3. Remove Component Framework Dependencies
- [x] Identify all uses of django-components and webcomponents
- [x] Convert component templates to standard Django includes
- [x] Update views that use component decorators
- [x] Remove django-components from INSTALLED_APPS and TEMPLATES settings
- [x] Remove django-components from requirements
- [ ] Update documentation on template patterns

### 4. Dependency Management with uv
- [x] Install uv tool globally (`pip install uv`)
- [x] Convert existing requirements files to uv format
- [x] Create requirements.txt generation script for deployments
- [x] Update documentation with new dependency management workflow
- [ ] Create pyproject.toml with project metadata
- [ ] Update build.sh script to use uv for dependency installation

### 5. App Restructuring
- [ ] Create new apps/ai/ directory structure
- [ ] Set up apps/ai/__init__.py, apps.py, models, views, and urls
- [ ] Create initial models for AI agent workflows
- [ ] Add apps.ai to INSTALLED_APPS
- [ ] Audit apps/communication for models and functionality to merge
- [ ] Migrate communication models to apps/common
- [ ] Update imports and references to communication models
- [ ] Remove apps/communication after successful migration

### 6. Team and Permission Models
- [x] Design Team model with fields for name, slug, and metadata
- [x] Create TeamMember model with role and permission fields
- [x] Implement Team-User relationship (many-to-many through TeamMember)
- [x] Add permission checking methods and decorators
- [x] Create migrations for new models
- [x] Add admin interface for Team management
- [ ] Implement basic Team-related views (create, join, manage)
- [x] Add tests for Team models and permissions
- [x] Improve test coverage for Team model to reach 100%

## Documentation
- [x] Update CLAUDE.md with development guidelines
- [x] Update CONTRIBUTING.md to match new project directions
- [ ] Create detailed setup guide for new developers
- [ ] Add example usage for each behavior mixin
- [ ] Document HTMX integration patterns with examples
- [ ] Add API documentation with OpenAPI/Swagger
- [ ] Create architecture diagram showing app relationships

## Infrastructure
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
- [ ] Setup pre-commit hooks for code quality (black, isort, flake8, mypy)
- [ ] Add GitHub Actions workflow for testing
- [ ] Create deployment pipeline for staging/production
- [ ] Setup monitoring and error tracking

## Code Quality
- [ ] Implement consistent error handling strategy
- [ ] Refactor redundant template logic
- [ ] Update to latest Django version
- [ ] Standardize form validation approach
- [ ] Improve type annotations across codebase

## Features
- [ ] Add user authentication templates (reset password, etc.)
- [ ] Implement custom admin dashboard
- [ ] Upgrade admin site to use Django Unfold with Tailwind integration
- [ ] Create reusable form components
- [ ] Add internationalization support
- [ ] Integrate payment processing example

## Frontend
- [ ] Modernize base templates with best practices
  - [ ] Create new _base.html template with improved structure
  - [ ] Design HTMX-focused partial templates for common UI elements
  - [ ] Implement template patterns from recent successful projects
  - [ ] Create reusable Tailwind UI components as includes
  - [ ] Document template extension and inclusion patterns
- [ ] Implement design system components
- [ ] Add JavaScript bundling with Webpack/Vite
- [ ] Create unified CSS approach (Tailwind only)
- [ ] Implement responsive layouts
- [ ] Add dark mode support