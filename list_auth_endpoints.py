#!/usr/bin/env python3
"""
List all available authentication endpoints
"""

import requests
import json
import sys

API_BASE_URL = "http://localhost:8000"

def list_auth_endpoints():
    """List all authentication endpoints from OpenAPI docs"""
    print("🔍 Listing Authentication Endpoints")
    print("=" * 50)
    
    try:
        # Get OpenAPI schema
        response = requests.get(f"{API_BASE_URL}/openapi.json")
        
        if response.status_code != 200:
            print(f"❌ Failed to get OpenAPI schema: {response.status_code}")
            return
        
        schema = response.json()
        paths = schema.get("paths", {})
        
        # Filter auth endpoints
        auth_endpoints = []
        
        for path, methods in paths.items():
            if "auth" in path:
                for method, details in methods.items():
                    auth_endpoints.append({
                        "path": path,
                        "method": method.upper(),
                        "summary": details.get("summary", "No description"),
                        "tags": details.get("tags", []),
                        "requires_auth": any(
                            security.get("bearerAuth", False) 
                            for security in details.get("security", [{}])
                        )
                    })
        
        # Sort endpoints
        auth_endpoints.sort(key=lambda x: (x["path"], x["method"]))
        
        # Print as table
        print(f"{'Method':<7} {'Path':<40} {'Auth':<5} {'Description'}")
        print("-" * 80)
        
        for endpoint in auth_endpoints:
            auth_required = "✓" if endpoint["requires_auth"] else "✗"
            print(f"{endpoint['method']:<7} {endpoint['path']:<40} {auth_required:<5} {endpoint['summary']}")
        
        print("\n🔐 Authentication Flow:")
        print("1. Register: POST /api/v1/auth/register")
        print("2. Login: POST /api/v1/auth/jwt/login")
        print("3. Use token in Authorization header: Bearer YOUR_TOKEN")
        print("4. Access protected endpoints")
        print("5. Logout: POST /api/v1/auth/jwt/logout")
        
        return auth_endpoints
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_health_check():
    """Test if the API is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/health")
        if response.status_code == 200:
            print("✅ API is running and healthy")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        return False

if __name__ == "__main__":
    print("🔐 Authentication Endpoints Listing Tool")
    print("=" * 50)
    
    # Check if API is running
    if not test_health_check():
        print("\nPlease make sure the API server is running:")
        print("python main.py")
        sys.exit(1)
    
    print()
    list_auth_endpoints()