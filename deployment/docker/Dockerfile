# Single-stage Docker build for Resume Job Matcher (simplified to fix spaCy model issue)
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd -r appuser && useradd -r -g appuser appuser

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir pydantic-settings

# Download spacy model
RUN python -m spacy download en_core_web_sm

# Verify spacy model installation
RUN python -c "import spacy; nlp = spacy.load('en_core_web_sm'); print('spaCy model loaded successfully')"

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

# Default command
CMD ["python", "main.py"]