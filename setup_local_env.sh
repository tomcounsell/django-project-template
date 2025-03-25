#!/bin/bash

# Django Project Template - Local Environment Setup Script
# This script sets up the local development environment and checks if all required settings are in place
# It is designed to be idempotent - running it multiple times should be safe

set -e

# Create a lock file to track what's been done in this run
LOCK_FILE=".setup_progress"
touch $LOCK_FILE

# Text formatting
BOLD="\033[1m"
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
RED="\033[0;31m"
NC="\033[0m" # No Color

# Helper functions
print_header() {
    echo -e "\n${BOLD}$1${NC}"
    echo "---------------------------------------------------------"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Start script
print_header "Django Project Template - Setup Script"
echo "This script will set up your local development environment."

# Step 1: Check Python version
print_header "1. Checking Python version"
python_version=$(python3 --version 2>&1)
if [[ $python_version == Python\ 3.* ]]; then
    version_number=${python_version:7}
    if (( $(echo "$version_number >= 3.9" | bc -l) )); then
        print_success "Python ${version_number} detected (recommended: 3.12)"
    else
        print_warning "Python ${version_number} detected. Recommended version is 3.9+ (ideally 3.12)."
    fi
else
    print_error "Python 3.x not found. Please install Python 3.9+ before continuing."
    exit 1
fi

# Step 2: Check PostgreSQL
print_header "2. Checking PostgreSQL"
if command -v pg_isready > /dev/null; then
    pg_status=$(pg_isready 2>&1)
    if [[ $pg_status == *"accepting connections"* ]]; then
        print_success "PostgreSQL is running"
    else
        print_warning "PostgreSQL is installed but not running. Please start PostgreSQL."
    fi
else
    print_warning "PostgreSQL command-line tools not found. Make sure PostgreSQL 14+ is installed."
fi

# Step 3: Check Node.js and npm
print_header "3. Checking Node.js and npm"
if command -v node > /dev/null; then
    node_version=$(node --version)
    print_success "Node.js ${node_version} detected"
    if command -v npm > /dev/null; then
        npm_version=$(npm --version)
        print_success "npm ${npm_version} detected"
    else
        print_warning "npm not found. Please install npm."
    fi
else
    print_warning "Node.js not found. It's recommended for frontend assets using Tailwind CSS."
fi

# Step 4: Set up virtual environment
print_header "4. Setting up Python virtual environment"
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    print_success "Virtual environment created."
else
    print_success "Virtual environment already exists."
fi

echo "Activating virtual environment..."
source venv/bin/activate
print_success "Virtual environment activated."

# Step 5: Install dependencies
print_header "5. Installing dependencies"

# Check if we've already done this step in a previous run
if grep -q "DEPENDENCIES_INSTALLED" $LOCK_FILE; then
    print_success "Dependencies were already installed in a previous run."
    echo "To reinstall dependencies, run: ./requirements/install.sh dev"
else
    echo "Installing uv package manager..."
    pip install uv
    print_success "uv installed."

    echo "Installing project dependencies..."
    if [ -f "requirements/install.sh" ]; then
        ./requirements/install.sh dev
        print_success "Dependencies installed successfully."
        # Mark this step as completed
        echo "DEPENDENCIES_INSTALLED=true" >> $LOCK_FILE
    else
        print_error "requirements/install.sh not found. Cannot install dependencies."
        exit 1
    fi
fi

# Step 6: Check environment files
print_header "6. Checking environment configuration"
if [ -f ".env.local" ]; then
    print_success ".env.local exists."
else
    echo "Creating .env.local from template..."
    if [ -f ".env.example" ]; then
        cp .env.example .env.local
        print_success ".env.local created from template. Please edit it with your settings."
    else
        print_error ".env.example not found. Cannot create .env.local."
        exit 1
    fi
fi

if [ -f "settings/local.py" ]; then
    print_success "settings/local.py exists."
else
    echo "Creating settings/local.py from template..."
    if [ -f "settings/local_template.py" ]; then
        cp settings/local_template.py settings/local.py
        print_success "settings/local.py created from template. Please edit if needed."
    else
        print_error "settings/local_template.py not found. Cannot create settings/local.py."
        exit 1
    fi
fi

# Step 7: Check .env.local required variables
print_header "7. Validating .env.local configuration"
env_file=".env.local"
required_vars=("SECRET_KEY" "DEBUG" "DATABASE_URL")
missing_vars=()

for var in "${required_vars[@]}"; do
    if ! grep -q "^${var}=" "$env_file" || grep -q "^${var}=$" "$env_file"; then
        missing_vars+=("$var")
    fi
done

if [ ${#missing_vars[@]} -eq 0 ]; then
    print_success "All required environment variables are set."
else
    print_warning "The following required variables are missing or empty in .env.local:"
    for var in "${missing_vars[@]}"; do
        echo " - $var"
    done
    echo "Please edit .env.local to set these variables."
fi

# Step 8: Check and setup database
print_header "8. Checking and setting up database"

# Try to extract database name from DATABASE_URL
db_name=""
if grep -q "^DATABASE_URL=" ".env.local"; then
    db_url=$(grep "^DATABASE_URL=" ".env.local" | cut -d'=' -f2)
    if [[ $db_url == postgres://* ]]; then
        # Extract DB name from postgres URL
        db_name=$(echo $db_url | sed -E 's/.*\/([^?]*).*/\1/')
        print_success "Found database name in .env.local: $db_name"
    fi
fi

# If we couldn't extract DB name or it's empty, ask the user
if [ -z "$db_name" ]; then
    # Check if we've already set up the database in this session
    if grep -q "DB_SETUP_COMPLETE" $LOCK_FILE; then
        print_warning "Database setup was already attempted but DATABASE_URL may be invalid."
        echo "Please edit .env.local manually to set a valid DATABASE_URL."
    else
        echo "What database name would you like to use for this project?"
        read -p "Database name [django_project_template]: " user_db_name
        db_name=${user_db_name:-django_project_template}
        
        # Ask for database username and password
        read -p "Database username [postgres]: " db_user
        db_user=${db_user:-postgres}
        
        read -s -p "Database password (input will be hidden): " db_password
        echo ""
        
        # Update the DATABASE_URL in .env.local
        if grep -q "^DATABASE_URL=" ".env.local"; then
            sed -i.bak "s|^DATABASE_URL=.*|DATABASE_URL=postgres://$db_user:$db_password@localhost:5432/$db_name|" ".env.local"
            rm -f ".env.local.bak"
        else
            echo "DATABASE_URL=postgres://$db_user:$db_password@localhost:5432/$db_name" >> ".env.local"
        fi
        print_success "Updated DATABASE_URL in .env.local"
        # Mark this step as completed
        echo "DB_SETUP_COMPLETE=true" >> $LOCK_FILE
    fi
fi

echo "Checking if database '$db_name' exists..."
if command -v psql > /dev/null; then
    if psql -lqt | cut -d \| -f 1 | grep -qw "$db_name"; then
        print_success "Database '$db_name' already exists."
    else
        echo "Database '$db_name' does not exist. Creating it now..."
        if createdb "$db_name"; then
            print_success "Database '$db_name' created successfully."
        else
            print_error "Failed to create database. Please create it manually:"
            echo "  createdb $db_name"
        fi
    fi
else
    print_warning "PostgreSQL client tools (psql) not found. Cannot check database."
    echo "Please ensure database '$db_name' exists before proceeding."
fi

echo "Attempting to connect to database..."
if python -c "from django.db import connection; connection.cursor()" 2>/dev/null; then
    print_success "Database connection successful."
else
    print_warning "Could not connect to database. Please check your database configuration in .env.local."
    echo "You may need to adjust database credentials or create the database manually."
fi

# Step 9: Run migrations
print_header "9. Setting up database schema"

# Check if we've already done this step in this run
if grep -q "MIGRATIONS_RUN" $LOCK_FILE; then
    print_success "Migrations were already run in this session."
else
    echo "Would you like to run database migrations? (y/n)"
    read run_migrations
    if [[ $run_migrations == "y" || $run_migrations == "Y" ]]; then
        echo "Running migrations..."
        python manage.py migrate
        print_success "Migrations completed."
        # Mark this step as completed
        echo "MIGRATIONS_RUN=true" >> $LOCK_FILE
    else
        print_warning "Skipping migrations. You'll need to run them manually:"
        echo "  python manage.py migrate"
    fi
fi

# Step 10: Check for superuser
print_header "10. Checking for superuser"
superuser_exists=$(python -c "import django; django.setup(); from django.contrib.auth import get_user_model; User = get_user_model(); print(User.objects.filter(is_superuser=True).exists())" 2>/dev/null)

if [ "$superuser_exists" = "True" ]; then
    print_success "Superuser already exists."
else
    echo "Would you like to create a superuser now? (y/n)"
    read create_superuser
    if [[ $create_superuser == "y" || $create_superuser == "Y" ]]; then
        python manage.py createsuperuser
    else
        print_warning "Skipping superuser creation. You can create one later with 'python manage.py createsuperuser'"
    fi
fi

# Step 11: Check frontend dependencies
print_header "11. Frontend dependencies check"
if [ -f "package.json" ]; then
    echo "Checking for frontend dependencies..."
    if [ -d "node_modules" ] && [ -f "node_modules/.package-lock.json" ]; then
        print_success "Frontend dependencies appear to be installed."
    else
        echo "Would you like to install frontend dependencies for Tailwind CSS? (y/n)"
        read install_frontend
        if [[ $install_frontend == "y" || $install_frontend == "Y" ]]; then
            npm install
            print_success "Frontend dependencies installed."
        else
            print_warning "Skipping frontend dependency installation."
            echo "Remember to run 'npm install' later if you need Tailwind CSS functionality."
        fi
    fi
else
    print_warning "No package.json found. Skipping frontend dependency check."
fi

# Final instructions
print_header "Setup Complete!"
echo -e "Your local development environment is now set up."
echo -e "\nTo start the development server, run:"
echo -e "  ${BOLD}python manage.py runserver${NC}"
echo -e "\nTo watch and compile CSS with Tailwind (in a separate terminal):"
echo -e "  ${BOLD}npm run watch:css${NC}"
echo -e "\nFor more information, check the documentation in docs/ and CLAUDE.md"

# Keep the lock file for future runs
echo -e "\nProgress tracking file created at ${LOCK_FILE}"
echo -e "This file helps avoid redundant operations if you run the script again."
echo -e "To force a fresh setup, delete this file before running the script again."