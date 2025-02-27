# Contributing to Django Project Template

Thank you for your interest in contributing to this Django project template! This document provides guidelines and instructions to help you get started.

## Getting Started

1. **Set up the project** by following the instructions in the [Quick Start Guide](README.md#quick-start-guide)

2. **Create a new branch** for your feature or bugfix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes** and ensure they follow the project's coding style

## Development Workflow

### Environment Variables

- Store all sensitive information and configuration in the `.env.local` file
- Never commit `.env.local` to version control
- Use `os.environ.get()` with sensible defaults for accessing environment variables
- Add new environment variables to `.env.example` with placeholder values

### Code Style

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) guidelines for Python code
- Use meaningful variable and function names
- Add docstrings to functions and classes

### Testing

- Write tests for new features or bug fixes
- Ensure all tests pass before submitting a pull request:
  ```bash
  python manage.py test
  ```

### Commit Messages

Write clear and meaningful commit messages that explain what changes were made and why:
```
Add user authentication to API endpoints

- Implemented token-based authentication for API
- Added decorators to secure sensitive endpoints
- Updated tests to include authentication
```

## Pull Request Process

1. **Update the README.md** if needed with details of changes to the interface
2. **Run tests** to make sure they pass
3. **Submit a pull request** to the main repository
4. **Describe your changes** in the pull request description
5. **Wait for review** from maintainers

## Adding New Features

When adding new features to the template:

1. **Keep it modular** - put code in the appropriate app directory
2. **Document it** - add comments and update README if necessary
3. **Add tests** - ensure good test coverage for new functionality
4. **Consider reusability** - make features generalizable when possible

## Reporting Issues

Please report bugs and suggest features using the issue tracker. Include:

- A clear and descriptive title
- Steps to reproduce the issue
- Expected behavior
- Actual behavior
- Screenshots if applicable

Thank you for contributing to making this project better!