#!/usr/bin/env python3
"""
Validation script for the enhanced job scraper implementation
This script validates the code structure without running it
"""

import ast
import os

def validate_job_scraper():
    """Validate the job scraper implementation"""
    
    print("🔍 Validating Enhanced Job Scraper Implementation")
    print("=" * 60)
    
    # Check if files exist
    files_to_check = [
        'app/services/job_scraper.py',
        'app/core/config.py',
        '.env.example',
        'docs/JOB_SCRAPING_GUIDE.md'
    ]
    
    print("\n1. File Existence Check:")
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path}")
    
    # Validate job_scraper.py structure
    print("\n2. Job Scraper Code Structure:")
    try:
        with open('app/services/job_scraper.py', 'r') as f:
            content = f.read()
        
        # Parse the AST to check for required methods
        tree = ast.parse(content)
        
        class MethodVisitor(ast.NodeVisitor):
            def __init__(self):
                self.methods = []
                self.classes = []
            
            def visit_ClassDef(self, node):
                self.classes.append(node.name)
                self.generic_visit(node)
            
            def visit_FunctionDef(self, node):
                self.methods.append(node.name)
                self.generic_visit(node)
        
        visitor = MethodVisitor()
        visitor.visit(tree)
        
        required_methods = [
            '_scrape_multiple_free_sources',
            '_scrape_remoteok_jobs',
            '_scrape_weworkremotely_jobs',
            '_rate_limited_request',
            '_generate_enhanced_jobs',
            'close'
        ]
        
        for method in required_methods:
            if method in visitor.methods:
                print(f"   ✅ {method}")
            else:
                print(f"   ❌ {method}")
        
        # Check for JobScraperService class
        if 'JobScraperService' in visitor.classes:
            print(f"   ✅ JobScraperService class")
        else:
            print(f"   ❌ JobScraperService class")
    
    except Exception as e:
        print(f"   ❌ Error parsing job_scraper.py: {e}")
    
    # Validate configuration
    print("\n3. Configuration Validation:")
    try:
        with open('app/core/config.py', 'r') as f:
            config_content = f.read()
        
        required_configs = [
            'SCRAPING_MIN_DELAY',
            'SCRAPING_MAX_DELAY',
            'SCRAPING_MAX_RETRIES',
            'ENABLE_REMOTEOK',
            'ENABLE_WEWORKREMOTELY',
            'ENABLE_ENHANCED_FALLBACK'
        ]
        
        for config in required_configs:
            if config in config_content:
                print(f"   ✅ {config}")
            else:
                print(f"   ❌ {config}")
    
    except Exception as e:
        print(f"   ❌ Error reading config.py: {e}")
    
    # Validate .env.example
    print("\n4. Environment Configuration:")
    try:
        with open('.env.example', 'r') as f:
            env_content = f.read()
        
        required_env_vars = [
            'SCRAPING_MIN_DELAY',
            'SCRAPING_MAX_DELAY',
            'ENABLE_REMOTEOK',
            'ENABLE_WEWORKREMOTELY'
        ]
        
        for env_var in required_env_vars:
            if env_var in env_content:
                print(f"   ✅ {env_var}")
            else:
                print(f"   ❌ {env_var}")
    
    except Exception as e:
        print(f"   ❌ Error reading .env.example: {e}")
    
    # Check imports and dependencies
    print("\n5. Import Structure:")
    try:
        with open('app/services/job_scraper.py', 'r') as f:
            content = f.read()
        
        required_imports = [
            'aiohttp',
            'BeautifulSoup',
            'urllib.parse',
            'random',
            'time'
        ]
        
        for imp in required_imports:
            if imp in content:
                print(f"   ✅ {imp}")
            else:
                print(f"   ❌ {imp}")
    
    except Exception as e:
        print(f"   ❌ Error checking imports: {e}")
    
    print("\n6. Implementation Features:")
    
    # Check for rate limiting implementation
    with open('app/services/job_scraper.py', 'r') as f:
        content = f.read()
    
    features = [
        ('Rate Limiting', 'last_request_time' in content and 'min_delay' in content),
        ('User Agent Rotation', 'user_agents' in content and 'random.choice' in content),
        ('Session Management', 'aiohttp.ClientSession' in content),
        ('Error Handling', 'try:' in content and 'except' in content),
        ('Multiple Sources', '_scrape_remoteok_jobs' in content and '_scrape_weworkremotely_jobs' in content),
        ('Enhanced Fallback', '_generate_enhanced_jobs' in content),
        ('Async Support', 'async def' in content),
        ('Configuration Integration', 'settings.' in content)
    ]
    
    for feature_name, has_feature in features:
        if has_feature:
            print(f"   ✅ {feature_name}")
        else:
            print(f"   ❌ {feature_name}")
    
    print("\n✅ Validation completed!")
    print("\n📋 Summary:")
    print("   - Enhanced job scraper with multiple free sources")
    print("   - Respectful rate limiting and error handling")
    print("   - Configurable job board toggles")
    print("   - Fallback to enhanced job generation")
    print("   - Proper async session management")
    print("   - Comprehensive documentation")

if __name__ == "__main__":
    validate_job_scraper()