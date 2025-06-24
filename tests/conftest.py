"""
Pytest configuration and fixtures
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """
    Create a test client for the FastAPI app
    """
    return TestClient(app)


@pytest.fixture
def sample_resume_text():
    """
    Sample resume text for testing
    """
    return """
    John Doe
    Software Engineer
    
    Experience: 5 years of experience in Python, JavaScript, and React.
    
    Skills:
    - Python
    - JavaScript
    - React
    - Node.js
    - PostgreSQL
    - AWS
    
    Education:
    Bachelor of Science in Computer Science
    """


@pytest.fixture
def sample_pdf_content():
    """
    Mock PDF content for testing
    """
    return b"Mock PDF content with resume data"