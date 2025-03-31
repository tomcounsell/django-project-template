#!/bin/bash

# Script to run HTMX interaction and responsive design tests
# Usage: ./run_htmx_tests.sh [--no-headless] [--type htmx|responsive|all]

# Default settings
HEADLESS="true"
TEST_TYPE="all"

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --no-headless)
      HEADLESS="false"
      shift
      ;;
    --type)
      TEST_TYPE="$2"
      shift 2
      ;;
    *)
      echo "Unknown argument: $1"
      exit 1
      ;;
  esac
done

# Validate test type
if [[ "$TEST_TYPE" != "htmx" && "$TEST_TYPE" != "responsive" && "$TEST_TYPE" != "all" ]]; then
  echo "Invalid test type: $TEST_TYPE. Use htmx, responsive, or all."
  exit 1
fi

# Set up environment
export DJANGO_SETTINGS_MODULE=settings
export TEST_HEADLESS=$HEADLESS

# Check if Django server is running
echo "Checking if Django server is running..."
SERVER_RUNNING=$(curl -s http://localhost:8000 > /dev/null && echo "yes" || echo "no")

# Start server if not running
if [[ "$SERVER_RUNNING" == "no" ]]; then
  echo "Starting Django server for tests..."
  python manage.py runserver --noreload > /dev/null 2>&1 &
  SERVER_PID=$!
  
  # Wait for server to start
  echo "Waiting for server to start..."
  sleep 2
  
  # Check if server started successfully
  if ! curl -s http://localhost:8000 > /dev/null; then
    echo "ERROR: Failed to start Django server."
    if [[ -n "$SERVER_PID" ]]; then
      kill $SERVER_PID
    fi
    exit 1
  fi
  
  echo "Server started with PID: $SERVER_PID"
else
  echo "Using existing Django server."
  SERVER_PID=""
fi

# Function to run tests
run_tests() {
  local type=$1
  echo "Running $type tests..."
  
  if [[ "$HEADLESS" == "false" ]]; then
    python tools/testing/test_manager.py run --category $type --verbose
  else
    python tools/testing/test_manager.py run --category $type
  fi
  
  return $?
}

# Run the requested tests
EXIT_CODE=0

case $TEST_TYPE in
  "htmx")
    run_tests htmx
    EXIT_CODE=$?
    ;;
  "responsive") 
    run_tests responsive
    EXIT_CODE=$?
    ;;
  "all")
    run_tests htmx
    HTMX_EXIT=$?
    
    run_tests responsive
    RESPONSIVE_EXIT=$?
    
    # Set exit code to non-zero if either test failed
    if [[ $HTMX_EXIT -ne 0 || $RESPONSIVE_EXIT -ne 0 ]]; then
      EXIT_CODE=1
    fi
    ;;
esac

# Stop server if we started it
if [[ -n "$SERVER_PID" ]]; then
  echo "Stopping Django server with PID: $SERVER_PID"
  kill $SERVER_PID
  wait $SERVER_PID 2>/dev/null
fi

echo "Tests completed with exit code: $EXIT_CODE"
exit $EXIT_CODE