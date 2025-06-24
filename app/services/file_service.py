"""
File handling service
"""

import io
import pdfplumber
from fastapi import UploadFile, HTTPException
from typing import Tuple
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class FileService:
    """
    Service for handling file operations
    """
    
    def __init__(self):
        self.max_file_size = settings.MAX_FILE_SIZE_MB * 1024 * 1024  # Convert to bytes
        self.allowed_types = settings.ALLOWED_FILE_TYPES
    
    def validate_file(self, file: UploadFile) -> None:
        """
        Validate uploaded file type and size
        
        Args:
            file: The uploaded file
            
        Raises:
            HTTPException: If file validation fails
        """
        # Validate file type
        if file.content_type not in self.allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Supported types: {', '.join(self.allowed_types)}. "
                       f"Received: {file.content_type}"
            )
        
        # Basic file size validation (this is approximate)
        if hasattr(file, 'size') and file.size and file.size > self.max_file_size:
            raise HTTPException(
                status_code=400,
                detail=f"File size too large. Maximum size: {settings.MAX_FILE_SIZE_MB}MB"
            )
    
    def extract_text_from_pdf(self, file_content: bytes) -> str:
        """
        Extract text from PDF file content
        
        Args:
            file_content: PDF file content as bytes
            
        Returns:
            Extracted text as string
            
        Raises:
            Exception: If PDF extraction fails
        """
        try:
            with pdfplumber.open(io.BytesIO(file_content)) as pdf:
                text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                
                extracted_text = text.strip()
                
                if not extracted_text:
                    raise ValueError("No text could be extracted from the PDF")
                
                return extracted_text
                
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            raise ValueError(f"Failed to extract text from PDF: {str(e)}")
    
    def extract_text_from_file(self, file_content: bytes, content_type: str) -> str:
        """
        Extract text from file based on content type
        
        Args:
            file_content: File content as bytes
            content_type: MIME type of the file
            
        Returns:
            Extracted text as string
        """
        if content_type == 'application/pdf':
            return self.extract_text_from_pdf(file_content)
        elif content_type == 'text/plain':
            try:
                text = file_content.decode('utf-8')
                if not text.strip():
                    raise ValueError("Text file is empty")
                return text
            except UnicodeDecodeError:
                try:
                    # Try with different encoding
                    text = file_content.decode('latin-1')
                    if not text.strip():
                        raise ValueError("Text file is empty")
                    return text
                except Exception as e:
                    raise ValueError(f"Failed to decode text file: {str(e)}")
        else:
            raise ValueError(f"Unsupported file type: {content_type}")
    
    def get_file_info(self, file: UploadFile, file_content: bytes) -> dict:
        """
        Get file information
        
        Args:
            file: The uploaded file
            file_content: File content as bytes
            
        Returns:
            Dictionary with file information
        """
        return {
            "filename": file.filename,
            "content_type": file.content_type,
            "size_bytes": len(file_content),
            "size_mb": round(len(file_content) / (1024 * 1024), 2)
        }