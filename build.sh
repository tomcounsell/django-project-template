#!/usr/bin/env bash
# exit on error
set -o errexit

# Install uv
pip install uv

# Generate requirements.txt if it doesn't exist
if [ ! -f requirements.txt ]; then
  ./requirements/generate_deployment_requirements.sh
fi

# Install dependencies from the generated requirements.txt
uv pip install -r requirements.txt

# Run Django commands
python manage.py collectstatic --no-input
python manage.py migrate