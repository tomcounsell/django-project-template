#!/bin/bash

# Script to generate requirements.txt for deployments

echo "Generating requirements.txt for deployment..."

# Copy the production lockfile to requirements.txt
cp requirements/prod.lock.txt requirements.txt

echo "Requirements.txt generated successfully!"
echo "File location: $(pwd)/requirements.txt"