# Resume Job Matcher

A production-ready FastAPI backend application that intelligently matches resumes to job listings using AI and machine learning.

## 🚀 Quick Start

```bash
# Clone and setup
git clone <repository-url>
cd resume-job-matcher
./scripts/setup.sh

# Start development server
./scripts/start_dev.sh
```

## 📋 Features

- **Smart Resume Analysis**: Extract skills, experience, and job titles using NLP
- **Intelligent Job Matching**: ML-powered similarity scoring with TF-IDF and cosine similarity
- **Asynchronous Processing**: Background job processing with Celery and Redis
- **Production Ready**: Docker, Kubernetes, monitoring, and comprehensive testing
- **RESTful API**: Well-documented FastAPI endpoints with automatic OpenAPI docs

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Client/User   │    │   FastAPI App   │    │  Celery Worker  │
│                 │    │                 │    │                 │
│ Upload Resume   │───▶│ /api/v1/jobs/   │───▶│ Process Resume  │
│ Check Status    │    │ /api/v1/tasks/  │    │ Extract Skills  │
│                 │    │                 │    │ Match Jobs      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
                                                       ▼
                                              ┌─────────────────┐
                                              │  Redis Broker   │
                                              │                 │
                                              │ Task Queue      │
                                              │ Result Storage  │
                                              └─────────────────┘
```

## 📁 Project Structure

```
resume-job-matcher/
├── app/                    # Main application package
│   ├── api/               # API routes and endpoints
│   ├── core/              # Core configuration and setup
│   ├── models/            # Pydantic models
│   ├── services/          # Business logic services
│   └── utils/             # Utility functions
├── data/                  # Data storage
│   ├── samples/          # Sample files
│   └── uploads/          # File uploads (if needed)
├── deployment/            # Deployment configurations
│   ├── docker/           # Docker files
│   └── kubernetes/       # Kubernetes manifests
├── docs/                  # Documentation
├── scripts/               # Utility scripts
├── tests/                 # Test files
├── main.py               # Application entry point
├── celery_worker.py      # Celery worker entry point
└── requirements.txt      # Python dependencies
```

## 🔧 Development

### Prerequisites

- Python 3.8+
- Redis 6.0+
- Git

### Setup

1. **Quick Setup**:
   ```bash
   ./scripts/setup.sh
   ```

2. **Manual Setup**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   python -m spacy download en_core_web_sm
   ```

3. **Start Services**:
   ```bash
   # Start Redis
   redis-server
   
   # Start Celery worker
   celery -A app.core.celery_app.celery_app worker --loglevel=info
   
   # Start API server
   python main.py
   ```

### API Endpoints

- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/v1/health/
- **Upload Resume**: `POST /api/v1/jobs/match`
- **Check Status**: `GET /api/v1/tasks/{task_id}/status`

## 🐳 Docker Deployment

```bash
# Development
docker-compose -f deployment/docker/docker-compose.yml up

# Production with monitoring
docker-compose -f deployment/docker/docker-compose.yml --profile monitoring up
```

## ☸️ Kubernetes Deployment

```bash
kubectl apply -f deployment/kubernetes/
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run specific test files
pytest tests/test_api.py
pytest tests/test_setup.py

# Run with coverage
pytest --cov=app tests/
```

## 📊 Monitoring

- **Flower (Celery)**: http://localhost:5555 (when using monitoring profile)
- **Health Checks**: Built-in health endpoints for Kubernetes
- **Logging**: Structured logging with configurable levels

## 🔒 Security

- Environment-based configuration
- Input validation and sanitization
- File type and size restrictions
- Non-root Docker containers
- Security headers and CORS configuration

## 📈 Performance

- Asynchronous processing with Celery
- Redis for fast caching and task queuing
- Optimized ML pipelines with scikit-learn
- Horizontal scaling support
- Resource limits and health checks

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📚 Documentation

- [Setup Instructions](docs/setup_instructions.md)
- [Project Overview](docs/PROJECT_OVERVIEW.md)
- [API Documentation](http://localhost:8000/docs) (when running)

## 🆘 Support

For issues and questions:
1. Check the [documentation](docs/)
2. Run the setup verification: `python tests/test_setup.py`
3. Check the health endpoint: `curl http://localhost:8000/api/v1/health/`
4. Open an issue on GitHub