#!/bin/bash

# Use uv to install dependencies
if [ "$1" == "dev" ]; then
  echo "Installing development dependencies..."
  uv pip install -r requirements/dev.lock.txt
elif [ "$1" == "prod" ]; then
  echo "Installing production dependencies..."
  uv pip install -r requirements/prod.lock.txt
else
  echo "Installing base dependencies..."
  uv pip install -r requirements/base.lock.txt
fi

echo "Dependencies installed successfully!"