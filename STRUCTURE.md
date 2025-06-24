# Resume Job Matcher - Project Structure

## 📁 Complete Directory Structure

```
resume-job-matcher/
├── 📄 README.md                           # Main project documentation
├── 📄 main.py                             # Application entry point
├── 📄 celery_worker.py                    # Celery worker entry point
├── 📄 requirements.txt                    # Python dependencies
├── 📄 .env.example                        # Environment variables template
├── 📄 .gitignore                          # Git ignore rules
├── 📄 STRUCTURE.md                        # This file
│
├── 📂 app/                                # Main application package
│   ├── 📄 __init__.py                     # Package initialization
│   ├── 📄 main.py                         # FastAPI app creation and configuration
│   │
│   ├── 📂 api/                            # API layer
│   │   ├── 📄 __init__.py
│   │   ├── 📄 routes.py                   # Main router configuration
│   │   └── 📂 endpoints/                  # API endpoints
│   │       ├── 📄 __init__.py
│   │       ├── 📄 health.py               # Health check endpoints
│   │       ├── 📄 jobs.py                 # Job matching endpoints
│   │       └── 📄 tasks.py                # Task management endpoints
│   │
│   ├── 📂 core/                           # Core application components
│   │   ├── 📄 __init__.py
│   │   ├── 📄 config.py                   # Application configuration
│   │   ├── 📄 logging.py                  # Logging configuration
│   │   └── 📄 celery_app.py               # Celery application setup
│   │
│   ├── 📂 models/                         # Pydantic models
│   │   ├── 📄 __init__.py
│   │   ├── 📄 job.py                      # Job-related models
│   │   ├── 📄 resume.py                   # Resume-related models
│   │   └── 📄 task.py                     # Task-related models
│   │
│   ├── 📂 services/                       # Business logic services
│   │   ├── 📄 __init__.py
│   │   ├── 📄 file_service.py             # File handling service
│   │   ├── 📄 nlp_service.py              # NLP and skill extraction
│   │   ├── 📄 job_scraper.py              # Job scraping service
│   │   ├── 📄 matching_service.py         # ML job matching service
│   │   └── 📄 tasks.py                    # Celery tasks
│   │
│   └── 📂 utils/                          # Utility functions
│       ├── 📄 __init__.py
│       ├── 📄 helpers.py                  # General helper functions
│       └── 📄 validators.py               # Validation utilities
│
├── 📂 data/                               # Data storage
│   ├── 📂 samples/                        # Sample files
│   │   └── 📄 sample_resume.txt           # Sample resume for testing
│   └── 📂 uploads/                        # File uploads directory
│       └── 📄 .gitkeep                    # Keep directory in git
│
├── 📂 deployment/                         # Deployment configurations
│   ├── 📂 docker/                         # Docker deployment
│   │   ├── 📄 Dockerfile                  # Multi-stage Docker build
│   │   └── 📄 docker-compose.yml          # Docker Compose configuration
│   └── 📂 kubernetes/                     # Kubernetes deployment
│       ├── 📄 namespace.yaml              # Kubernetes namespace
│       └── 📄 redis.yaml                  # Redis deployment
│
├── 📂 docs/                               # Documentation
│   ├── 📄 README.md                       # Detailed README
│   ├── 📄 setup_instructions.md           # Setup guide
│   └── 📄 PROJECT_OVERVIEW.md             # Architecture overview
│
├── 📂 scripts/                            # Utility scripts
│   ├── 📄 setup.sh                        # Project setup script
│   └── 📄 start_dev.sh                    # Development startup script
│
├── 📂 tests/                              # Test files
│   ├── 📄 __init__.py
│   ├── 📄 conftest.py                     # Pytest configuration
│   ├── 📄 test_setup.py                   # Setup verification tests
│   └── 📄 test_api.py                     # API integration tests
│
└── 📂 logs/                               # Log files directory
    └── 📄 .gitkeep                        # Keep directory in git
```

## 🏗️ Architecture Components

### **API Layer** (`app/api/`)
- **FastAPI Routes**: RESTful endpoints for resume upload and job matching
- **Request/Response Models**: Pydantic models for data validation
- **Error Handling**: Comprehensive error handling and HTTP status codes

### **Core Layer** (`app/core/`)
- **Configuration Management**: Environment-based settings with Pydantic
- **Celery Setup**: Async task processing configuration
- **Logging**: Structured logging with rotation and levels

### **Models Layer** (`app/models/`)
- **Job Models**: Job details, search queries, and match results
- **Resume Models**: Resume data, extracted skills, and upload metadata
- **Task Models**: Task status, progress tracking, and responses

### **Services Layer** (`app/services/`)
- **File Service**: PDF/text extraction and validation
- **NLP Service**: Skill extraction using spaCy and pattern matching
- **Job Scraper**: Job listing retrieval (mock and real implementations)
- **Matching Service**: ML-based job matching with TF-IDF and cosine similarity
- **Celery Tasks**: Background processing workflows

### **Utils Layer** (`app/utils/`)
- **Validators**: Input validation and sanitization
- **Helpers**: Common utility functions and data processing

## 🔄 Data Flow

1. **Resume Upload** → API validates file → Triggers Celery task
2. **Text Extraction** → Service extracts text from PDF/TXT files
3. **Skill Analysis** → NLP service extracts skills using spaCy
4. **Job Search** → Scraper service finds relevant job listings
5. **ML Matching** → Matching service calculates similarity scores
6. **Results** → Ranked job matches returned to client

## 🚀 Deployment Options

### **Development**
```bash
./scripts/setup.sh      # Initial setup
./scripts/start_dev.sh  # Start development server
```

### **Docker**
```bash
docker-compose -f deployment/docker/docker-compose.yml up
```

### **Kubernetes**
```bash
kubectl apply -f deployment/kubernetes/
```

## 🧪 Testing Strategy

- **Unit Tests**: Individual component testing
- **Integration Tests**: End-to-end API testing
- **Setup Verification**: Dependency and configuration validation
- **Health Checks**: System component monitoring

## 📊 Monitoring & Observability

- **Health Endpoints**: `/api/v1/health/` for system status
- **Celery Monitoring**: Flower dashboard for task monitoring
- **Structured Logging**: JSON logs with correlation IDs
- **Metrics**: Prometheus-compatible metrics (future)

## 🔒 Security Features

- **Input Validation**: File type and size restrictions
- **Environment Configuration**: Secure credential management
- **CORS Configuration**: Cross-origin request handling
- **Non-root Containers**: Security-hardened Docker images

This structure provides a scalable, maintainable, and production-ready foundation for the Resume Job Matcher application.