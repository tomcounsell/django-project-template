#!/bin/bash
#
# Test runner script for the Django Project Template.
#
# This script provides a convenient interface to run_tests.py.
# It handles setting Django settings and passing command-line arguments.

# Set Django settings module if not set
export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-settings}"

# Parse command line arguments
COVERAGE=0
HTML_REPORT=0
XML_REPORT=0
BROWSER=0
NO_HEADLESS=0
SLOW_MO=0
BROWSER_TYPE="chromium"
VERBOSE=0
TEST_TYPE="all"

while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        --coverage)
            COVERAGE=1
            shift
            ;;
        --html-report)
            HTML_REPORT=1
            shift
            ;;
        --xml-report)
            XML_REPORT=1
            shift
            ;;
        --browser)
            BROWSER=1
            shift
            ;;
        --no-headless)
            NO_HEADLESS=1
            shift
            ;;
        --slow-mo)
            SLOW_MO="$2"
            shift 2
            ;;
        --browser-type)
            BROWSER_TYPE="$2"
            shift 2
            ;;
        --verbose|-v)
            VERBOSE=1
            shift
            ;;
        --type)
            TEST_TYPE="$2"
            shift 2
            ;;
        *)
            # Unknown option
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Validate test type
if [[ ! "$TEST_TYPE" =~ ^(unit|integration|e2e|visual|api|all)$ ]]; then
    echo "Invalid test type: $TEST_TYPE"
    echo "Valid options: unit, integration, e2e, visual, api, all"
    exit 1
fi

# Build the command
CMD="python run_tests.py --type $TEST_TYPE"

if [[ $COVERAGE -eq 1 ]]; then
    CMD="$CMD --coverage"
fi

if [[ $HTML_REPORT -eq 1 ]]; then
    CMD="$CMD --html-report"
fi

if [[ $XML_REPORT -eq 1 ]]; then
    CMD="$CMD --xml-report"
fi

if [[ $BROWSER -eq 1 ]]; then
    CMD="$CMD --browser"
fi

if [[ $NO_HEADLESS -eq 1 ]]; then
    CMD="$CMD --no-headless"
fi

if [[ $SLOW_MO -ne 0 ]]; then
    CMD="$CMD --slow-mo $SLOW_MO"
fi

if [[ "$BROWSER_TYPE" != "chromium" ]]; then
    CMD="$CMD --browser-type $BROWSER_TYPE"
fi

if [[ $VERBOSE -eq 1 ]]; then
    CMD="$CMD --verbose"
fi

# Run the command
echo "Running: $CMD"
$CMD