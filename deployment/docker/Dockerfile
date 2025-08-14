# Multi-stage Docker build for Resume Job Matcher
# This Dockerfile creates an optimized production image

# Build stage
FROM python:3.11-slim as builder

WORKDIR /app

# Install system dependencies needed for building
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt
RUN pip install --no-cache-dir --user pydantic-settings

# Download spacy model
ENV PATH=/root/.local/bin:$PATH
RUN python -m spacy download en_core_web_sm

# Verify spacy model installation
RUN python -c "import spacy; nlp = spacy.load('en_core_web_sm'); print('spaCy model loaded successfully')"

# Production stage
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean \
    && groupadd -r appuser && useradd -r -g appuser appuser

# Copy Python packages and spaCy models from builder stage
COPY --from=builder /root/.local /home/appuser/.local

# Set PATH for user packages
ENV PATH=/home/appuser/.local/bin:$PATH

# Copy entrypoint script
COPY deployment/docker/docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Copy application code
COPY . .

# Create necessary directories and set permissions
RUN mkdir -p data/uploads data/samples logs \
    && chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health/ || exit 1

# Set entrypoint
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]

# Default command
CMD ["python", "main.py"]