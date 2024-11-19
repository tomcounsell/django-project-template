# Scheduled Tasks for Generative AI Dockerfile
# This container uses a multi-stage build process:
#   1. Builder stage: Compiles Python packages with required system dependencies;
#   2. Final stage: Creates a lean runtime image with only the necessary components.

# Runtime Details:
#   - Base: Python 3.8 Alpine
#   - Database: PostgreSQL
#   - Web Server: Gunicorn
#   - Port: 8000

# Build stage for compiling dependencies
FROM python:3.8-alpine as builder

# Set core environment variables for Python optimization
# Prevent Python from writing pyc files (compiled bytecode) to disk, reducing container size and improving startup time
ENV PYTHONDONTWRITEBYTECODE=1
# Ensure Python output is sent straight to terminal without being buffered
ENV PYTHONUNBUFFERED=1

# Install necessary build dependencies
RUN apk add --no-cache \
    build-base \
    gcc \
    libpq \
    linux-headers \
    musl-dev \
    postgresql-dev

# Set builder working directory
WORKDIR /build

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Final stage - this will be your actual container
FROM python:3.8-alpine

# Set core environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install only runtime dependencies
RUN apk add --no-cache \
    libpq

# Set container working directory
WORKDIR /app

# Copy only the compiled packages from builder
COPY --from=builder /usr/local/lib/python3.8/site-packages/ /usr/local/lib/python3.8/site-packages/

# Copy the application code
COPY . .

# Gather all project static assets (CSS, JS, images, etc.) and place them in the STATIC_ROOT directory for production
RUN python manage.py collectstatic --noinput

# Set the default Gunicorn command for the web service and bind to port 8000
CMD ["gunicorn", "--bind", ":8000", "settings.wsgi:application"]
