#!/usr/bin/env python3
"""
Check if required dependencies are installed
"""

import sys

def check_dependency(module_name, package_name=None):
    """Check if a dependency is installed"""
    if package_name is None:
        package_name = module_name
    
    try:
        __import__(module_name)
        print(f"✅ {package_name} is installed")
        return True
    except ImportError:
        print(f"❌ {package_name} is NOT installed")
        return False

def main():
    """Check all required dependencies"""
    print("🔍 Checking Dependencies")
    print("=" * 30)
    
    dependencies = [
        ("fastapi", "fastapi"),
        ("uvicorn", "uvicorn"),
        ("pydantic", "pydantic"),
        ("celery", "celery"),
        ("redis", "redis"),
        ("aiohttp", "aiohttp"),
        ("spacy", "spacy"),
        ("sklearn", "scikit-learn"),
        ("numpy", "numpy"),
        ("bs4", "beautifulsoup4"),
        ("requests", "requests"),
    ]
    
    missing = []
    installed = []
    
    for module, package in dependencies:
        if check_dependency(module, package):
            installed.append(package)
        else:
            missing.append(package)
    
    print(f"\n📊 Summary:")
    print(f"   Installed: {len(installed)}")
    print(f"   Missing: {len(missing)}")
    
    if missing:
        print(f"\n❌ Missing dependencies:")
        for dep in missing:
            print(f"   - {dep}")
        
        print(f"\n💡 To install missing dependencies:")
        print(f"   pip install {' '.join(missing)}")
        print(f"   OR")
        print(f"   pip install -r requirements.txt")
        
        return False
    else:
        print(f"\n✅ All dependencies are installed!")
        return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)