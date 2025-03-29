Installation
============

This guide will help you set up and run the Django Project Template on your local machine.

Prerequisites
------------

* Python 3.10 or higher
* PostgreSQL 13 or higher
* Node.js and npm (for Tailwind CSS)

Quick Start
----------

1. Clone the repository:

.. code-block:: bash

    git clone https://github.com/yourusername/django-project-template.git
    cd django-project-template

2. Run the setup script:

.. code-block:: bash

    source setup_local_env.sh

This script will:

* Create and activate a virtual environment
* Install dependencies using uv
* Set up your local environment variables
* Run database migrations
* Start the development server

Manual Setup
-----------

If you prefer to set up manually, follow these steps:

1. Create a virtual environment:

.. code-block:: bash

    python -m venv venv
    source venv/bin/activate

2. Install uv and dependencies:

.. code-block:: bash

    pip install uv
    ./requirements/install.sh dev

3. Configure your environment:

.. code-block:: bash

    cp .env.example .env.local
    # Edit .env.local with your settings

4. Run migrations:

.. code-block:: bash

    python manage.py migrate

5. Start the development server:

.. code-block:: bash

    python manage.py runserver

Configuration
------------

Key environment variables:

* ``DEBUG``: Enable debug mode (set to True for development)
* ``SECRET_KEY``: Django secret key
* ``DATABASE_URL``: PostgreSQL connection string
* ``AWS_*``: AWS credentials for S3 storage
* ``STRIPE_*``: Stripe API keys for payment processing
* ``TWILIO_*``: Twilio credentials for SMS