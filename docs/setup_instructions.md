# Detailed Setup Instructions

## System Requirements

- **Python**: 3.8 or higher
- **Redis**: 6.0 or higher
- **Operating System**: Windows, macOS, or Linux
- **Memory**: At least 4GB RAM recommended
- **Storage**: 1GB free space

## Step-by-Step Setup

### 1. Python Environment Setup

#### Option A: Using Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv resume_matcher_env

# Activate virtual environment
# On Windows:
resume_matcher_env\Scripts\activate
# On macOS/Linux:
source resume_matcher_env/bin/activate

# Verify Python version
python --version  # Should be 3.8+
```

#### Option B: Using Conda
```bash
# Create conda environment
conda create -n resume_matcher python=3.9

# Activate environment
conda activate resume_matcher
```

### 2. Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install all dependencies
pip install -r requirements.txt

# Verify installation
pip list
```

### 3. Install Spacy Language Model

```bash
# Download English language model
python -m spacy download en_core_web_sm

# Verify installation
python -c "import spacy; nlp = spacy.load('en_core_web_sm'); print('Spacy model loaded successfully')"
```

### 4. Redis Setup

#### Option A: Local Installation

**On macOS (using Homebrew):**
```bash
# Install Redis
brew install redis

# Start Redis service
brew services start redis

# Verify Redis is running
redis-cli ping  # Should return "PONG"
```

**On Ubuntu/Debian:**
```bash
# Update package list
sudo apt update

# Install Redis
sudo apt install redis-server

# Start Redis service
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Verify Redis is running
redis-cli ping  # Should return "PONG"
```

**On Windows:**
```bash
# Download Redis for Windows from:
# https://github.com/microsoftarchive/redis/releases

# Or use Windows Subsystem for Linux (WSL)
# Or use Docker (see Option B below)
```

#### Option B: Using Docker (Recommended for Windows)
```bash
# Pull Redis image
docker pull redis:alpine

# Run Redis container
docker run -d --name redis-server -p 6379:6379 redis:alpine

# Verify Redis is running
docker exec redis-server redis-cli ping  # Should return "PONG"
```

### 5. Verify Installation

Create a test script to verify all components:

```python
# test_setup.py
import sys
import redis
import spacy
import pdfplumber
import sklearn
from celery import Celery

def test_python_version():
    print(f"Python version: {sys.version}")
    assert sys.version_info >= (3, 8), "Python 3.8+ required"
    print("✓ Python version OK")

def test_redis_connection():
    try:
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        print("✓ Redis connection OK")
    except Exception as e:
        print(f"✗ Redis connection failed: {e}")
        return False
    return True

def test_spacy_model():
    try:
        nlp = spacy.load("en_core_web_sm")
        doc = nlp("This is a test.")
        print("✓ Spacy model OK")
    except Exception as e:
        print(f"✗ Spacy model failed: {e}")
        return False
    return True

def test_other_imports():
    try:
        import fastapi
        import uvicorn
        import pydantic
        import beautifulsoup4
        import requests
        print("✓ All imports OK")
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False
    return True

if __name__ == "__main__":
    print("Testing setup...")
    test_python_version()
    test_redis_connection()
    test_spacy_model()
    test_other_imports()
    print("Setup verification complete!")
```

Run the test:
```bash
python test_setup.py
```

## Running the Application

### 1. Start Redis (if not already running)
```bash
# Local Redis
redis-server

# Or Docker Redis
docker start redis-server
```

### 2. Start Celery Worker

Open a new terminal and activate your virtual environment:
```bash
# Activate virtual environment
source resume_matcher_env/bin/activate  # On Windows: resume_matcher_env\Scripts\activate

# Start Celery worker
celery -A tasks.celery_app worker --loglevel=info

# You should see output like:
# [2024-01-01 12:00:00,000: INFO/MainProcess] Connected to redis://localhost:6379/0
# [2024-01-01 12:00:00,000: INFO/MainProcess] mingle: searching for neighbors
# [2024-01-01 12:00:00,000: INFO/MainProcess] mingle: all alone
# [2024-01-01 12:00:00,000: INFO/MainProcess] celery@hostname ready.
```

### 3. Start FastAPI Server

Open another terminal and activate your virtual environment:
```bash
# Activate virtual environment
source resume_matcher_env/bin/activate  # On Windows: resume_matcher_env\Scripts\activate

# Start FastAPI server
python main.py

# Or using uvicorn directly:
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# You should see output like:
# INFO:     Started server process [12345]
# INFO:     Waiting for application startup.
# INFO:     Application startup complete.
# INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### 4. Test the API

Open a third terminal to test the API:

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test with a sample text file
echo "Software Engineer with 5 years of experience in Python, JavaScript, and React. Worked on web applications and APIs." > sample_resume.txt

# Upload resume
curl -X POST "http://localhost:8000/api/match-jobs" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@sample_resume.txt"

# Note the task_id from the response, then check status
curl -X GET "http://localhost:8000/api/task-status/YOUR_TASK_ID" \
     -H "accept: application/json"
```

## Troubleshooting

### Common Issues and Solutions

#### 1. ModuleNotFoundError
```bash
# Error: No module named 'spacy'
# Solution: Ensure virtual environment is activated and dependencies are installed
pip install -r requirements.txt
```

#### 2. Spacy Model Not Found
```bash
# Error: Can't find model 'en_core_web_sm'
# Solution: Download the model
python -m spacy download en_core_web_sm
```

#### 3. Redis Connection Error
```bash
# Error: redis.exceptions.ConnectionError
# Solution: Start Redis server
redis-server
# Or check if Redis is running on correct port
redis-cli -p 6379 ping
```

#### 4. Celery Worker Not Starting
```bash
# Error: Celery worker fails to start
# Solution: Check Redis connection and Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
celery -A tasks.celery_app worker --loglevel=info
```

#### 5. Port Already in Use
```bash
# Error: Port 8000 is already in use
# Solution: Use a different port
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

#### 6. File Upload Issues
```bash
# Error: 422 Unprocessable Entity
# Solution: Ensure file is PDF or TXT format and not empty
file sample_resume.txt  # Check file type
ls -la sample_resume.txt  # Check file size
```

### Performance Optimization

#### 1. Celery Worker Scaling
```bash
# Run multiple workers
celery -A tasks.celery_app worker --loglevel=info --concurrency=4

# Or run multiple worker processes
celery multi start worker1 worker2 -A tasks.celery_app --loglevel=info
```

#### 2. Redis Configuration
```bash
# Edit redis.conf for production
maxmemory 256mb
maxmemory-policy allkeys-lru
```

#### 3. FastAPI Configuration
```python
# In main.py, add for production:
app = FastAPI(
    title="Resume Job Matcher API",
    description="A backend service for matching resumes to job listings using AI",
    version="1.0.0",
    docs_url="/docs" if DEBUG else None,  # Disable docs in production
    redoc_url="/redoc" if DEBUG else None
)
```

## Production Deployment

### Using Docker

Create `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt
RUN python -m spacy download en_core_web_sm

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  redis:
    image: redis:alpine
    ports:
      - "6379:6379"

  web:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - redis
    environment:
      - REDIS_URL=redis://redis:6379/0

  worker:
    build: .
    command: celery -A tasks.celery_app worker --loglevel=info
    depends_on:
      - redis
    environment:
      - REDIS_URL=redis://redis:6379/0
```

Deploy:
```bash
docker-compose up -d
```

### Environment Variables for Production

Create `.env` file:
```env
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
DEBUG=False
MAX_FILE_SIZE_MB=10
ALLOWED_ORIGINS=https://yourdomain.com
```

## Monitoring and Logging

### Celery Monitoring
```bash
# Install flower for Celery monitoring
pip install flower

# Start flower
celery -A tasks.celery_app flower

# Access at http://localhost:5555
```

### Application Logging
```python
# Add to main.py
import logging
from logging.handlers import RotatingFileHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler('app.log', maxBytes=10485760, backupCount=5),
        logging.StreamHandler()
    ]
)
```

This completes the detailed setup instructions for the Resume Job Matcher backend application.