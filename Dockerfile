# Scheduled Tasks for Generative AI Project Dockerfile

# This container uses a multi-stage build process:
#   1. Builder stage: Compiles Python packages with required system dependencies;
#   2. Final stage: Creates a lean runtime image with only the necessary components.

# Runtime Details:
#   - Base: Python 3.11 Alpine
#   - Database: PostgreSQL
#   - Cache: Redis, Redis Streams
#   - Schedulers: Celery, Django-Q2
#   - Web Server: Gunicorn
#   - Port: 8000

# Build stage for compiling dependencies
FROM python:3.11-alpine AS builder

# Set core environment variables for Python optimization
# Prevent Python from writing pyc files (compiled bytecode) to disk, reducing container size and improving startup time
ENV PYTHONDONTWRITEBYTECODE=1
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

# Install Python dependencies and upgrade Pip
COPY requirements.txt .

# Install Python dependencies using a local Asian mirror and increased timeout
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir --default-timeout=100 -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

# ---------------------------------------------------
# Final stage for runtime image
FROM python:3.11-alpine

# Accept and set the SECRET_KEY
ARG DJANGO_SECRET_KEY
ENV DJANGO_SECRET_KEY=${DJANGO_SECRET_KEY}

# Set core environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Add /app/venv/bin to PATH for runtime
ENV PATH="/app/venv/bin:$PATH"

RUN echo "Build DJANGO_SECRET_KEY: $DJANGO_SECRET_KEY"

# Install only runtime dependencies
RUN apk add --no-cache \
    libpq \
    redis  # Added Redis CLI for debugging Redis connections

# Set container working directory
WORKDIR /app

# Copy only the compiled packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/

# Copy application code
COPY . .

# Create static directory
RUN mkdir -p /app/static

# Skip collectstatic during build (as it will run at runtime)
ENV DJANGO_SKIP_COLLECTSTATIC=1

# Create and switch to non-root user for security
RUN addgroup -S app && adduser -S app -G app
RUN chown -R app:app /app
USER app

# Set the default command
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "settings.wsgi:application"]