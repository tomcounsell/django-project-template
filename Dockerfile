# Dockerfile for ScheduledTasks AI Service
# This container runs a Python web application using Gunicorn and PostgreSQL
# Required environment variables:
#   - SECRET_KEY: Django secret key
#   - DATABASE_URL: PostgreSQL connection string
# Exposes port 8000 for the web service

# Use the Alpine base image for Python 3.8
FROM python:3.8-alpine

# Set core environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies for PostgreSQL
RUN apk update && apk add --no-cache \
    build-base \
    postgresql-dev \
    libpq \
    gcc \
    musl-dev \
    linux-headers

# Set container working directory
WORKDIR /app

# Copy requirements.txt to leverage Docker cached layer
COPY requirements.txt /app/w

# Install Python dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the application code
COPY . /app/

# Collect static files
RUN python manage.py collectstatic --noinput

# Set the default Gunicorn command for the web service and bind to port 8000
CMD ["gunicorn", "--bind", ":8000", "settings.wsgi:application"]
