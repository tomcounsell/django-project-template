# Repository Cleanup Guide

This document outlines the cleanup process to make the repository more maintainable and tidy.

## 1. Test Runner Consolidation

Three separate test runners have been consolidated into a single unified script:

- `run_htmx_tests.sh`
- `test.sh` 
- `run_tests.py`

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

## 2. Files to Remove

These files are no longer needed and can be safely removed:

```
run_htmx_tests.sh
test.sh
run_tests.py
```

## 3. Gitignore Updates

The `.gitignore-update` file contains additional entries to be added to the main `.gitignore` file.
This will prevent unnecessary files from being committed to the repository.

## 4. Temporary Directories to Clean

These directories should not be in version control:

```
__pycache__/
.idea/
.mypy_cache/
.pytest_cache/
reports/
test_reports/
test_screenshots/
```

They are now properly included in the updated `.gitignore`.

## Implementation Steps

1. Add the new unified test runner: `test_runner.py`
2. Update the `.gitignore` file with the entries from `.gitignore-update`
3. Remove redundant test scripts
4. Add CLEANUP.md to document the changes

These changes will make the repository more maintainable and reduce clutter.