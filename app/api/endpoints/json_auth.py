"""
JSON-compatible authentication endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Optional

from app.auth.manager import auth_backend, fastapi_users
from app.models.user import User

router = APIRouter()

class LoginRequest(BaseModel):
    """JSON login request model"""
    username: str
    password: str

class LoginResponse(BaseModel):
    """Login response model"""
    access_token: str
    token_type: str

@router.post("/json-login", response_model=LoginResponse)
async def json_login(
    login_data: LoginRequest,
):
    """
    Login endpoint that accepts JSON data
    """
    # Convert JSON request to form data
    form_data = OAuth2PasswordRequestForm(
        username=login_data.username,
        password=login_data.password,
        scope=""
    )
    
    # Use the same authentication as the regular login endpoint
    try:
        # Get the login route from fastapi-users
        login_route = None
        for route in fastapi_users.get_auth_router(auth_backend).routes:
            if route.path == "/login" and "POST" in route.methods:
                login_route = route
                break
        
        if not login_route:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Login route not found"
            )
        
        # Call the login route with form data
        response = await login_route.endpoint(form_data)
        return response
        
    except HTTPException as e:
        # Re-raise the exception
        raise e
    except Exception as e:
        # Handle other exceptions
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )