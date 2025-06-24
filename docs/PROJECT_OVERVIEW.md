# Resume Job Matcher - Project Overview

## Project Description

The Resume Job Matcher is a backend application built with FastAPI that automatically matches resumes to relevant job listings using machine learning and natural language processing. The system processes uploaded resumes, extracts skills and experience, scrapes job listings, and uses similarity algorithms to find the best job matches.

## Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Client/User   │    │   FastAPI App   │    │  Celery Worker  │
│                 │    │                 │    │                 │
│ Upload Resume   │───▶│ /api/match-jobs │───▶│ Process Resume  │
│ Check Status    │    │ /api/task-status│    │ Extract Skills  │
│                 │    │                 │    │ Scrape Jobs     │
└─────────────────┘    └─────────────────┘    │ Match Jobs      │
                                              └─────────────────┘
                                                       │
                                                       ▼
                                              ┌─────────────────┐
                                              │  Redis Broker   │
                                              │                 │
                                              │ Task Queue      │
                                              │ Result Storage  │
                                              └─────────────────┘
```

## Technology Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **Celery**: Distributed task queue for asynchronous processing
- **Redis**: Message broker and result backend
- **Spacy**: Advanced NLP library for skill extraction
- **Scikit-learn**: Machine learning library for job matching
- **PDFPlumber**: PDF text extraction
- **BeautifulSoup**: Web scraping (mock implementation)
- **Pydantic**: Data validation and serialization

## File Structure

```
resume-job-matcher/
├── main.py                 # FastAPI application with API endpoints
├── tasks.py                # Celery tasks for background processing
├── models.py               # Pydantic models for data validation
├── celery_config.py        # Celery configuration
├── requirements.txt        # Python dependencies
├── test_setup.py          # Setup verification script
├── test_api.py            # API integration tests
├── sample_resume.txt      # Sample resume for testing
├── README.md              # Main documentation
├── setup_instructions.md  # Detailed setup guide
└── PROJECT_OVERVIEW.md    # This file
```

## Key Components

### 1. FastAPI Application (main.py)

**Endpoints:**
- `POST /api/match-jobs`: Upload resume and start processing
- `GET /api/task-status/{task_id}`: Check task status and get results
- `GET /health`: Health check with Celery worker status
- `GET /`: Basic API information

**Features:**
- File upload validation (PDF/TXT, size limits)
- Asynchronous task management
- Error handling and logging
- CORS support for frontend integration

### 2. Celery Tasks (tasks.py)

**Main Task: `process_resume_and_match_jobs`**
1. **Text Extraction**: Extract text from PDF or text files
2. **Skill Extraction**: Use NLP to identify technical skills and job titles
3. **Job Scraping**: Fetch relevant job listings (mock implementation)
4. **Job Matching**: Calculate similarity scores using TF-IDF and cosine similarity
5. **Result Filtering**: Return top matches above similarity threshold

**NLP Processing:**
- Technical skill recognition (Python, JavaScript, React, etc.)
- Job title extraction (Software Engineer, Data Scientist, etc.)
- Experience years extraction
- Entity recognition using Spacy

### 3. Data Models (models.py)

**Key Models:**
- `JobDetail`: Job information with similarity score
- `TaskStatusResponse`: Task status and results
- `ExtractedSkills`: Skills and titles from resume
- `TaskStatus`: Enum for task states

### 4. Configuration (celery_config.py)

**Celery Settings:**
- Redis broker configuration
- Task serialization (JSON)
- Timeout settings (30 minutes)
- Worker optimization settings

## Workflow

### 1. Resume Upload
```python
# Client uploads resume
POST /api/match-jobs
Content-Type: multipart/form-data
File: resume.pdf

# Response
{
  "task_id": "abc123-def456-ghi789",
  "status": "started",
  "message": "Resume uploaded successfully. Job matching in progress."
}
```

### 2. Background Processing
```python
# Celery worker processes the resume
1. Extract text from PDF/TXT
2. Analyze text with Spacy NLP
3. Extract skills: ["Python", "React", "AWS", ...]
4. Extract job titles: ["Software Engineer", ...]
5. Search for jobs using extracted skills
6. Calculate similarity scores
7. Filter and rank results
```

### 3. Status Checking
```python
# Client checks task status
GET /api/task-status/abc123-def456-ghi789

# Response (in progress)
{
  "task_id": "abc123-def456-ghi789",
  "status": "STARTED",
  "progress": "Calculating job matches..."
}

# Response (completed)
{
  "task_id": "abc123-def456-ghi789",
  "status": "SUCCESS",
  "result": [
    {
      "title": "Senior Python Developer",
      "company": "Tech Corp",
      "location": "San Francisco, CA",
      "description": "We are looking for a skilled Python developer...",
      "url": "https://example.com/job1",
      "similarity_score": 0.85
    }
  ]
}
```

## Machine Learning Pipeline

### 1. Text Preprocessing
- Convert resume and job descriptions to lowercase
- Remove stop words and special characters
- Tokenize text into meaningful units

### 2. Feature Extraction
```python
# TF-IDF Vectorization
vectorizer = TfidfVectorizer(
    max_features=1000,
    stop_words='english',
    ngram_range=(1, 2),  # Unigrams and bigrams
    lowercase=True
)
```

### 3. Similarity Calculation
```python
# Cosine Similarity
similarities = cosine_similarity(resume_vector, job_vectors)
```

### 4. Ranking and Filtering
- Filter jobs with similarity > threshold (0.1)
- Sort by similarity score (highest first)
- Return top 5 matches

## Skill Extraction Algorithm

### 1. Predefined Skills Database
```python
technical_skills = {
    'python', 'java', 'javascript', 'react', 'angular',
    'aws', 'docker', 'kubernetes', 'sql', 'mongodb',
    # ... 50+ technical skills
}
```

### 2. Pattern Matching
```python
# Job title patterns
job_title_patterns = [
    r'software engineer', r'data scientist',
    r'full stack developer', r'devops engineer'
]
```

### 3. NLP Entity Recognition
```python
# Use Spacy for entity extraction
doc = nlp(resume_text)
for ent in doc.ents:
    if ent.label_ in ['ORG', 'PRODUCT']:
        # Potential skill or technology
```

### 4. Experience Extraction
```python
# Extract years of experience
experience_pattern = r'(\d+)\s*(?:years?|yrs?)\s*(?:of\s*)?(?:experience|exp)'
```

## Production Considerations

### 1. Scalability
- **Horizontal Scaling**: Multiple Celery workers
- **Load Balancing**: Multiple FastAPI instances
- **Database**: PostgreSQL for persistent storage
- **Caching**: Redis for frequently accessed data

### 2. Security
- **Authentication**: JWT tokens or OAuth2
- **File Validation**: Strict file type and size checking
- **Rate Limiting**: Prevent API abuse
- **Input Sanitization**: Prevent injection attacks

### 3. Monitoring
- **Logging**: Structured logging with correlation IDs
- **Metrics**: Prometheus/Grafana for monitoring
- **Health Checks**: Comprehensive system health monitoring
- **Error Tracking**: Sentry for error reporting

### 4. Job Scraping
- **Official APIs**: Use Indeed API, LinkedIn API instead of scraping
- **Rate Limiting**: Respect API rate limits
- **Legal Compliance**: Follow terms of service
- **Data Quality**: Validate and clean scraped data

## Testing Strategy

### 1. Unit Tests
```bash
pytest tests/test_tasks.py
pytest tests/test_models.py
pytest tests/test_main.py
```

### 2. Integration Tests
```bash
python test_api.py  # End-to-end API testing
```

### 3. Setup Verification
```bash
python test_setup.py  # Verify all dependencies
```

## Deployment Options

### 1. Docker Deployment
```bash
docker-compose up -d
```

### 2. Cloud Deployment
- **AWS**: ECS/Fargate + ElastiCache + RDS
- **GCP**: Cloud Run + Memorystore + Cloud SQL
- **Azure**: Container Instances + Redis Cache + PostgreSQL

### 3. Kubernetes
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: resume-matcher-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: resume-matcher-api
  template:
    spec:
      containers:
      - name: api
        image: resume-matcher:latest
        ports:
        - containerPort: 8000
```

## Performance Metrics

### Expected Performance
- **Resume Processing**: 5-15 seconds per resume
- **Concurrent Users**: 100+ with proper scaling
- **File Size Limit**: 10MB per resume
- **Job Matching**: 5-10 jobs per skill query

### Optimization Opportunities
- **Caching**: Cache job listings and skill extractions
- **Batch Processing**: Process multiple resumes together
- **Model Optimization**: Use faster NLP models
- **Database Indexing**: Optimize job search queries

## Future Enhancements

### 1. Advanced ML Features
- **Deep Learning**: Use BERT/GPT for better text understanding
- **Recommendation System**: Collaborative filtering
- **Skill Similarity**: Semantic skill matching
- **Career Path Analysis**: Suggest career progression

### 2. Additional Features
- **Resume Builder**: Generate optimized resumes
- **Interview Preparation**: Match-based interview questions
- **Salary Estimation**: Predict salary ranges
- **Company Insights**: Company culture and reviews

### 3. API Enhancements
- **Webhooks**: Real-time notifications
- **Batch API**: Process multiple resumes
- **Analytics API**: Usage statistics and insights
- **Admin API**: System management endpoints

This comprehensive overview provides a complete understanding of the Resume Job Matcher backend system, its architecture, implementation details, and production considerations.