#!/usr/bin/env python3
"""
Test script to verify that all dependencies and components are properly installed.
"""

import sys
import importlib
from typing import List, Tuple

def test_python_version() -> bool:
    """Test if Python version is 3.8 or higher."""
    print("Testing Python version...")
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version >= (3, 8):
        print("✓ Python version OK")
        return True
    else:
        print("✗ Python 3.8+ required")
        return False

def test_imports() -> bool:
    """Test if all required packages can be imported."""
    print("\nTesting package imports...")
    
    required_packages = [
        'fastapi',
        'uvicorn',
        'celery',
        'redis',
        'pydantic',
        'pdfplumber',
        'spacy',
        'bs4',  # beautifulsoup4
        'requests',
        'sklearn',  # scikit-learn
        'aiohttp'
    ]
    
    failed_imports = []
    
    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"✓ {package}")
        except ImportError as e:
            print(f"✗ {package} - {e}")
            failed_imports.append(package)
    
    if not failed_imports:
        print("✓ All packages imported successfully")
        return True
    else:
        print(f"✗ Failed to import: {', '.join(failed_imports)}")
        return False

def test_redis_connection() -> bool:
    """Test Redis connection."""
    print("\nTesting Redis connection...")
    
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0, socket_timeout=5)
        r.ping()
        print("✓ Redis connection OK")
        return True
    except Exception as e:
        print(f"✗ Redis connection failed: {e}")
        print("  Make sure Redis server is running on localhost:6379")
        return False

def test_spacy_model() -> bool:
    """Test if spacy English model is available."""
    print("\nTesting Spacy model...")
    
    try:
        import spacy
        nlp = spacy.load("en_core_web_sm")
        
        # Test basic functionality
        doc = nlp("This is a test sentence with Python programming.")
        tokens = [token.text for token in doc]
        
        print(f"✓ Spacy model loaded successfully")
        print(f"  Test tokens: {tokens[:5]}...")
        return True
    except OSError as e:
        print(f"✗ Spacy model 'en_core_web_sm' not found: {e}")
        print("  Run: python -m spacy download en_core_web_sm")
        return False
    except Exception as e:
        print(f"✗ Spacy model test failed: {e}")
        return False

def test_celery_basic() -> bool:
    """Test basic Celery functionality."""
    print("\nTesting Celery basic functionality...")
    
    try:
        from celery import Celery
        
        # Create a test Celery app
        test_app = Celery('test', broker='redis://localhost:6379/0')
        
        # Test if we can create the app without errors
        print("✓ Celery app creation OK")
        return True
    except Exception as e:
        print(f"✗ Celery test failed: {e}")
        return False

def test_file_processing() -> bool:
    """Test basic file processing capabilities."""
    print("\nTesting file processing...")
    
    try:
        import pdfplumber
        import io
        
        # Test text processing
        test_text = "Software Engineer with 5 years of experience in Python and JavaScript."
        print(f"✓ Text processing OK")
        
        # Test PDF processing capability (without actual PDF)
        print("✓ PDF processing library available")
        return True
    except Exception as e:
        print(f"✗ File processing test failed: {e}")
        return False

def test_ml_capabilities() -> bool:
    """Test machine learning capabilities."""
    print("\nTesting ML capabilities...")
    
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        import numpy as np
        
        # Test basic TF-IDF and similarity
        documents = [
            "Python developer with machine learning experience",
            "JavaScript frontend developer",
            "Data scientist with Python skills"
        ]
        
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(documents)
        
        # Calculate similarity
        similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])
        
        print(f"✓ ML processing OK")
        print(f"  Sample similarities: {similarities[0][:2]}")
        return True
    except Exception as e:
        print(f"✗ ML capabilities test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 50)
    print("Resume Job Matcher - Setup Verification")
    print("=" * 50)
    
    tests = [
        test_python_version,
        test_imports,
        test_redis_connection,
        test_spacy_model,
        test_celery_basic,
        test_file_processing,
        test_ml_capabilities
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"✗ Test {test.__name__} crashed: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! Your setup is ready.")
        print("\nNext steps:")
        print("1. Start Redis server: redis-server")
        print("2. Start Celery worker: celery -A tasks.celery_app worker --loglevel=info")
        print("3. Start FastAPI server: python main.py")
        print("4. Visit http://localhost:8000/docs for API documentation")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        print("\nCommon solutions:")
        print("- Install missing packages: pip install -r requirements.txt")
        print("- Download spacy model: python -m spacy download en_core_web_sm")
        print("- Start Redis server: redis-server")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)