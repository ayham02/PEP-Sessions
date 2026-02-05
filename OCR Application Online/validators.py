import os
import mimetypes
from typing import Tuple
from fastapi import UploadFile, HTTPException
from config import settings

class FileValidator:
    """Validates uploaded files for security and compatibility"""
    
    @staticmethod
    def validate_file_size(file: UploadFile) -> None:
        """Validate file size doesn't exceed maximum"""
        # Read file to check size
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Reset to beginning
        
        if file_size > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File size exceeds maximum allowed size of {settings.MAX_FILE_SIZE / (1024*1024)}MB"
            )
    
    @staticmethod
    def validate_file_extension(filename: str) -> None:
        """Validate file has an allowed extension"""
        _, ext = os.path.splitext(filename.lower())
        
        if ext not in settings.allowed_extensions_list:
            raise HTTPException(
                status_code=400,
                detail=f"File extension '{ext}' not allowed. Allowed extensions: {', '.join(settings.allowed_extensions_list)}"
            )
    
    @staticmethod
    def validate_mime_type(file: UploadFile) -> None:
        """Validate file MIME type"""
        content_type = file.content_type
        
        if content_type not in settings.allowed_mime_types_list:
            raise HTTPException(
                status_code=400,
                detail=f"MIME type '{content_type}' not allowed. Allowed types: {', '.join(settings.allowed_mime_types_list)}"
            )
    
    @staticmethod
    def validate_filename(filename: str) -> str:
        """Sanitize and validate filename"""
        if not filename:
            raise HTTPException(status_code=400, detail="Filename cannot be empty")
        
        # Remove path components for security
        filename = os.path.basename(filename)
        
        # Remove any potentially dangerous characters
        safe_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._- ")
        filename = ''.join(c for c in filename if c in safe_chars)
        
        if not filename:
            raise HTTPException(status_code=400, detail="Invalid filename")
        
        return filename
    
    @classmethod
    def validate_upload(cls, file: UploadFile) -> Tuple[str, str]:
        """
        Perform all validations on uploaded file
        Returns: (sanitized_filename, file_extension)
        """
        if not file:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Validate and sanitize filename
        safe_filename = cls.validate_filename(file.filename)
        
        # Validate extension
        cls.validate_file_extension(safe_filename)
        
        # Validate MIME type
        cls.validate_mime_type(file)
        
        # Validate file size
        cls.validate_file_size(file)
        
        # Get extension
        _, ext = os.path.splitext(safe_filename.lower())
        
        return safe_filename, ext
