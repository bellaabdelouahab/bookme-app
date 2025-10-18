# syntax=docker/dockerfile:1
# Multi-stage build for optimized production image

# =============================================================================
# Base Stage - Common dependencies
# =============================================================================
FROM python:3.11-slim as base

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# =============================================================================
# Builder Stage - Install Python dependencies
# =============================================================================
FROM base as builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY pyproject.toml ./

# Install Python dependencies
RUN pip install --upgrade pip setuptools wheel && \
    pip install -e ".[prod]"

# =============================================================================
# Development Stage
# =============================================================================
FROM base as development

# Install development system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY pyproject.toml ./

# Install all dependencies including dev
RUN pip install --upgrade pip setuptools wheel && \
    pip install -e ".[dev]"

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 bookme && \
    chown -R bookme:bookme /app

USER bookme

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health/')" || exit 1

# Run development server
CMD ["python", "src/manage.py", "runserver", "0.0.0.0:8000"]

# =============================================================================
# Production Stage
# =============================================================================
FROM base as production

# Copy Python dependencies from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 bookme && \
    mkdir -p /app/logs /app/staticfiles /app/media && \
    chown -R bookme:bookme /app

# Collect static files
RUN python src/manage.py collectstatic --noinput --settings=bookme.settings.production || true

USER bookme

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health/')" || exit 1

# Run with Gunicorn
CMD ["gunicorn", \
    "--chdir", "src", \
    "--bind", "0.0.0.0:8000", \
    "--workers", "4", \
    "--worker-class", "sync", \
    "--worker-tmp-dir", "/dev/shm", \
    "--max-requests", "1000", \
    "--max-requests-jitter", "50", \
    "--timeout", "60", \
    "--access-logfile", "-", \
    "--error-logfile", "-", \
    "--log-level", "info", \
    "bookme.wsgi:application"]
