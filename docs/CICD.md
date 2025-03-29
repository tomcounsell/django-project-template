# CI/CD Configuration

This project uses Continuous Integration and Continuous Deployment workflows to automate testing, linting, building, and deployment processes.

## GitHub Actions

The project includes several GitHub Actions workflows:

### 1. Test Workflow (`test.yml`)

- **Trigger**: Runs on pushes and pull requests to the `main` branch
- **Jobs**:
  - Spins up a PostgreSQL database service
  - Runs all tests with pytest and generates coverage reports
  - Uploads coverage results to Codecov

### 2. Lint and Security Workflow (`lint.yml`)

- **Trigger**: Runs on pushes and pull requests to the `main` branch
- **Jobs**:
  - **Lint**: Checks code formatting (Black), import ordering (isort), linting (flake8), and type hints (mypy)
  - **Security**: Scans code for security vulnerabilities (Bandit) and checks dependencies for known vulnerabilities (Safety)

### 3. Build Workflow (`build.yml`)

- **Trigger**: Runs on pushes and pull requests to the `main` branch
- **Jobs**:
  - **Build Python Package**: Creates distributable Python package artifacts
  - **Build Frontend**: Compiles and minimizes frontend assets (CSS)
  - **Build Docker**: Creates a Docker image using the Python package and frontend assets

### 4. Documentation Workflow (`docs.yml`)

- **Trigger**: Runs on pushes and pull requests to the `main` branch when files in the `apps/` or `docs/` directories change
- **Jobs**:
  - Builds Sphinx documentation
  - Deploys documentation to GitHub Pages (only from the `main` branch)

## GitLab CI

An alternative GitLab CI configuration is also provided in `.gitlab-ci.yml`:

- **Stages**: lint → test → build → deploy
- **Features**:
  - Runs linting, security checks, and tests
  - Builds Python package, frontend assets, and Docker image
  - Supports deployment to staging and production environments
  - Includes caching for dependencies to speed up builds

## Setting Up CI/CD

### GitHub Actions

1. **Repository Secrets**:
   - `CODECOV_TOKEN`: Token for uploading coverage reports to Codecov

2. **GitHub Pages** (for documentation):
   - In your repository settings, enable GitHub Pages
   - Select the source as "GitHub Actions"

### GitLab CI

1. **Variables**:
   - `CI_REGISTRY_USER` and `CI_REGISTRY_PASSWORD`: For Docker registry access
   - `STAGING_DEPLOY_WEBHOOK` and `PRODUCTION_DEPLOY_WEBHOOK`: Optional webhook URLs for deployment

2. **Runner Setup**:
   - Ensure your GitLab runner has Docker support if you're using the Docker image building feature

## Local CI Testing

To test CI workflows locally before pushing changes:

1. **Pre-commit Hooks**:
   ```bash
   # Install pre-commit hooks
   ./docs/scripts/install-hooks.sh
   
   # Run pre-commit on all files
   pre-commit run --all-files
   ```

2. **Tests with Coverage**:
   ```bash
   DJANGO_SETTINGS_MODULE=settings pytest --cov=apps
   ```

3. **Build Documentation**:
   ```bash
   ./docs/scripts/build_all_docs.sh
   ```

## Deployment Environments

The CI/CD setup supports multiple deployment environments:

- **Staging**: Automatically deployed from the `main` branch
- **Production**: Deployed from git tags

## References

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GitLab CI Documentation](https://docs.gitlab.com/ee/ci/)
- [Codecov Documentation](https://docs.codecov.io/)