# ============================================
# CONTACT INTELLIGENCE MODULE - DOCKERFILE
# ============================================
# Multi-stage build for production-ready container
# Optimized for size and security
# ============================================

# === STAGE 1: Builder ===
FROM python:3.11-slim as builder

LABEL maintainer="Super Brain Team"
LABEL description="Contact Intelligence Service - Builder Stage"

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    make \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create working directory
WORKDIR /build

# Copy requirements first (for layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --user --no-warn-script-location -r requirements.txt

# Download spaCy models
RUN python -m spacy download en_core_web_sm && \
    python -m spacy download ru_core_news_sm

# === STAGE 2: Runtime ===
FROM python:3.11-slim

LABEL maintainer="Super Brain Team"
LABEL version="1.0.0"
LABEL description="Contact Intelligence Service - Production"

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH=/root/.local/bin:$PATH \
    APP_HOME=/app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
RUN useradd -m -u 1000 -s /bin/bash appuser

# Create app directory
WORKDIR $APP_HOME

# Copy Python packages from builder
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY main.py .
COPY .env.example .env.example

# Create directories for logs and data
RUN mkdir -p logs data && \
    chown -R appuser:appuser $APP_HOME

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]

# ============================================
# BUILD INSTRUCTIONS:
# ============================================
#
# 1. Build the image:
#    docker build -t contact-intelligence:latest .
#
# 2. Run locally for testing:
#    docker run -p 8000:8000 --env-file .env contact-intelligence:latest
#
# 3. Push to registry:
#    docker tag contact-intelligence:latest registry.digitalocean.com/your-registry/contact-intelligence:latest
#    docker push registry.digitalocean.com/your-registry/contact-intelligence:latest
#
# 4. Build with specific version:
#    docker build -t contact-intelligence:v1.0.0 .
#
# 5. Multi-platform build (for ARM64 + AMD64):
#    docker buildx build --platform linux/amd64,linux/arm64 -t contact-intelligence:latest .
#
# ============================================
