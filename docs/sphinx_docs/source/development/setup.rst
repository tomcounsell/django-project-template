Development Setup
===============

Setting up your development environment for the Django Project Template.

Prerequisites
------------

- Python 3.10 or higher
- PostgreSQL 13 or higher
- Node.js and npm (for Tailwind CSS)

Local Environment
---------------

1. Clone the repository:

.. code-block:: bash

    git clone https://github.com/yourusername/django-project-template.git
    cd django-project-template

2. Run the setup script:

.. code-block:: bash

    source setup_local_env.sh

This script creates a virtual environment, installs dependencies, and sets up your local configuration.

Manual Setup
-----------

If you prefer to set up manually:

.. code-block:: bash

    # Create and activate virtual environment
    python -m venv venv
    source venv/bin/activate
    
    # Install dependencies with uv
    pip install uv
    ./requirements/install.sh dev
    
    # Configure environment variables
    cp .env.example .env.local
    # Edit .env.local with your settings
    
    # Run migrations
    python manage.py migrate
    
    # Run server
    python manage.py runserver

VSCode Setup
-----------

For VSCode users, the following extensions are recommended:

- Python
- Django
- Tailwind CSS IntelliSense
- Black Formatter
- isort