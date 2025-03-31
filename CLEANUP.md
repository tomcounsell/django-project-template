# Repository Cleanup Guide

This document outlines how the repository has been cleaned up to make it more maintainable and tidy.

## 1. Test Runner Consolidation

Three separate test runners have been consolidated into a single unified script:

- ✅ Removed: `run_htmx_tests.sh`
- ✅ Removed: `test.sh` 
- ✅ Removed: `run_tests.py`

**Replaced with**: `test_runner.py`

The consolidated test runner supports all previous functionality with a cleaner interface:

```bash
# Run all tests
./test_runner.py

# Run with coverage
./test_runner.py --coverage

# Run specific test types
./test_runner.py --type unit
./test_runner.py --type e2e --no-headless

# Run tests with HTML coverage report
./test_runner.py --coverage --html-report
```

## 2. Gitignore Updates

The `.gitignore` file has been updated to better exclude temporary files and directories:

- Test artifacts: `reports/`, `test_reports/`, `test_screenshots/`
- Development environment: `.venv/`, `venv/`, `.env.*`
- IDE files: `.idea/`, `.vscode/`, `*.code-workspace`
- Cache directories: `__pycache__/`, `.mypy_cache/`, `.pytest_cache/`
- Temporary files: `*.swp`, `*.swo`, `*~`

## 3. About pyproject.toml

The `pyproject.toml` file serves multiple purposes:

1. **Tool Configuration**: Consolidates settings for black, isort, mypy, and pytest
2. **Dependency Management**: Organizes project dependencies and optional dependency groups
3. **Project Metadata**: Provides basic project information

While it can be used for packaging, here it primarily serves as a central configuration file, replacing multiple tool-specific config files.

## 4. Benefits of the Cleanup

- ✅ **Simplified Testing**: One consistent interface for all test types
- ✅ **Reduced Clutter**: Removed redundant scripts 
- ✅ **Better Ignorables**: Improved .gitignore to prevent committing temporary files
- ✅ **Clean History**: Future commits will be cleaner with proper ignores

The repository is now more maintainable with less duplication and better organization.