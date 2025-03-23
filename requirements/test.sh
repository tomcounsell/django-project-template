#!/bin/bash

echo "Testing uv environment setup..."

# Create a temporary virtual environment
python3 -m venv .uv_test_venv
source .uv_test_venv/bin/activate

# Install uv
pip install uv

# Install dependencies
uv pip install -r requirements/dev.lock.txt

# Test Django installation
python -c "import django; print(f'Django {django.__version__} installed successfully')"

# Test that other key packages are installed
python -c "import rest_framework; print('Django REST framework installed successfully')"
python -c "import django_extensions; print('Django Extensions installed successfully')"
python -c "import django_components; print('Django Components installed successfully')"

# Cleanup
deactivate
rm -rf .uv_test_venv

echo "Test completed successfully!"