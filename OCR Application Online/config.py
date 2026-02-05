import os
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    """Application configuration settings"""
    
    # Application
    APP_NAME: str = "OCR Web Application"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # CORS
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173,http://127.0.0.1:3000"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(',')]
    
    # File Upload
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: str = ".png,.jpg,.jpeg,.pdf"
    ALLOWED_MIME_TYPES: str = "image/png,image/jpeg,image/jpg,application/pdf"
    
    @property
    def allowed_extensions_list(self) -> List[str]:
        """Parse allowed extensions from comma-separated string"""
        return [ext.strip() for ext in self.ALLOWED_EXTENSIONS.split(',')]
    
    @property
    def allowed_mime_types_list(self) -> List[str]:
        """Parse allowed MIME types from comma-separated string"""
        return [mime.strip() for mime in self.ALLOWED_MIME_TYPES.split(',')]
    
    # OCR Settings
    TESSERACT_LANG: str = "eng"
    TESSERACT_CONFIG: str = "--oem 3 --psm 3"
    
    # Temporary Storage
    TEMP_DIR: str = "/tmp/ocr_uploads"
    
    # Processing
    MAX_IMAGE_DIMENSION: int = 4000
    TARGET_DPI: int = 300
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance
settings = Settings()

# Ensure temp directory exists
os.makedirs(settings.TEMP_DIR, exist_ok=True)
