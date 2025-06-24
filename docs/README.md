# Resume Job Matcher Backend

A FastAPI-based backend application that matches resumes to job listings using AI and machine learning techniques.

## Features

- **Resume Upload**: Accept PDF or text resume files
- **Skill Extraction**: Use NLP to extract skills and job titles from resumes
- **Job Scraping**: Fetch relevant job listings (mock implementation for demo)
- **Job Matching**: Use TF-IDF and cosine similarity to match jobs to resumes
- **Asynchronous Processing**: Use Celery for background task processing
- **Real-time Status**: Track job matching progress with task status endpoints

## Architecture

- **FastAPI**: Web framework for API endpoints
- **Celery**: Asynchronous task queue for background processing
- **Redis**: Message broker and result backend for Celery
- **Spacy**: NLP library for skill extraction
- **Scikit-learn**: Machine learning library for job matching

## Directory Structure

```
resume-job-matcher/
├── main.py              # FastAPI application with API endpoints
├── tasks.py             # Celery tasks for resume processing and job matching
├── models.py            # Pydantic models for API requests/responses
├── celery_config.py     # Celery configuration
├── requirements.txt     # Python dependencies
├── README.md           # This file
└── setup_instructions.md # Detailed setup guide
```

## Quick Start

### Prerequisites

- Python 3.8+
- Redis server
- Git

### Installation

1. **Clone the repository** (if applicable):
   ```bash
   git clone <repository-url>
   cd resume-job-matcher
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Download Spacy model**:
   ```bash
   python -m spacy download en_core_web_sm
   ```

5. **Start Redis server**:
   ```bash
   # On macOS with Homebrew:
   brew services start redis
   
   # On Ubuntu/Debian:
   sudo systemctl start redis-server
   
   # Using Docker:
   docker run -d -p 6379:6379 redis:alpine
   ```

### Running the Application

1. **Start Celery worker** (in one terminal):
   ```bash
   celery -A tasks.celery_app worker --loglevel=info
   ```

2. **Start FastAPI server** (in another terminal):
   ```bash
   python main.py
   # or
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

3. **Access the API**:
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

## API Endpoints

### POST /api/match-jobs
Upload a resume and start job matching process.

**Request:**
- File: Resume file (PDF or TXT)

**Response:**
```json
{
  "task_id": "abc123-def456-ghi789",
  "status": "started",
  "message": "Resume uploaded successfully. Job matching in progress."
}
```

### GET /api/task-status/{task_id}
Check the status of a job matching task.

**Response:**
```json
{
  "task_id": "abc123-def456-ghi789",
  "status": "SUCCESS",
  "result": [
    {
      "title": "Software Engineer - Python",
      "company": "Tech Corp",
      "location": "San Francisco, CA",
      "description": "We are looking for a skilled software engineer...",
      "url": "https://example.com/job1",
      "similarity_score": 0.85
    }
  ]
}
```

## Usage Example

```bash
# Upload resume
curl -X POST "http://localhost:8000/api/match-jobs" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@resume.pdf"

# Check task status
curl -X GET "http://localhost:8000/api/task-status/your-task-id" \
     -H "accept: application/json"
```

## Configuration

### Environment Variables

You can configure the application using environment variables:

- `REDIS_URL`: Redis connection URL (default: redis://localhost:6379/0)
- `CELERY_BROKER_URL`: Celery broker URL (default: redis://localhost:6379/0)
- `CELERY_RESULT_BACKEND`: Celery result backend URL (default: redis://localhost:6379/0)

### Production Considerations

1. **Database**: Consider using PostgreSQL with SQLAlchemy for storing job matches
2. **Job Scraping**: Use official APIs (Indeed API, LinkedIn API) instead of web scraping
3. **File Storage**: Use cloud storage (AWS S3, Google Cloud Storage) instead of in-memory processing
4. **Security**: Implement authentication and authorization
5. **Monitoring**: Add logging, metrics, and health checks
6. **Scaling**: Use multiple Celery workers and Redis clustering

## Development

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest
```

### Code Quality
```bash
# Install development dependencies
pip install black flake8 mypy

# Format code
black .

# Lint code
flake8 .

# Type checking
mypy .
```

## Troubleshooting

### Common Issues

1. **Spacy model not found**:
   ```bash
   python -m spacy download en_core_web_sm
   ```

2. **Redis connection error**:
   - Ensure Redis server is running
   - Check Redis connection URL

3. **Celery worker not starting**:
   - Check Redis connection
   - Verify Python path includes project directory

4. **File upload errors**:
   - Check file size limits
   - Verify file type (PDF or TXT only)

## License

This project is for educational/demonstration purposes.