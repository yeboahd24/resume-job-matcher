"""
Validation utilities
"""

import re
from typing import List, Optional
from fastapi import HTTPException


def validate_email(email: str) -> bool:
    """
    Validate email format
    
    Args:
        email: Email address to validate
        
    Returns:
        True if valid, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_file_extension(filename: str, allowed_extensions: List[str]) -> bool:
    """
    Validate file extension
    
    Args:
        filename: Name of the file
        allowed_extensions: List of allowed extensions (e.g., ['.pdf', '.txt'])
        
    Returns:
        True if extension is allowed, False otherwise
    """
    if not filename:
        return False
    
    file_extension = filename.lower().split('.')[-1]
    return f'.{file_extension}' in [ext.lower() for ext in allowed_extensions]


def validate_task_id(task_id: str) -> bool:
    """
    Validate Celery task ID format
    
    Args:
        task_id: Task ID to validate
        
    Returns:
        True if valid format, False otherwise
    """
    # Celery task IDs are typically UUIDs
    uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    return re.match(uuid_pattern, task_id.lower()) is not None


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing potentially dangerous characters
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove path separators and other dangerous characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove leading/trailing dots and spaces
    sanitized = sanitized.strip('. ')
    
    # Ensure filename is not empty
    if not sanitized:
        sanitized = 'unnamed_file'
    
    return sanitized


def validate_similarity_threshold(threshold: float) -> float:
    """
    Validate and clamp similarity threshold
    
    Args:
        threshold: Similarity threshold value
        
    Returns:
        Valid threshold value (0.0 - 1.0)
        
    Raises:
        HTTPException: If threshold is invalid
    """
    if not isinstance(threshold, (int, float)):
        raise HTTPException(
            status_code=400,
            detail="Similarity threshold must be a number"
        )
    
    if threshold < 0.0 or threshold > 1.0:
        raise HTTPException(
            status_code=400,
            detail="Similarity threshold must be between 0.0 and 1.0"
        )
    
    return float(threshold)