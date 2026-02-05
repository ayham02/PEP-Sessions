import os
import uuid
import logging
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import aiofiles
from typing import Dict

from config import settings
from validators import FileValidator
from ocr_processor import OCRProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize OCR processor
ocr_processor = OCRProcessor()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Temporary directory: {settings.TEMP_DIR}")
    yield
    # Shutdown
    logger.info("Shutting down application")

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Modern OCR Web Application - Extract text from images and PDFs",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "OCR Web Application API",
        "version": settings.APP_VERSION,
        "status": "online"
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION
    }

@app.get("/api/languages")
async def get_supported_languages():
    """Get list of supported OCR languages"""
    # In production, you could query Tesseract for available languages
    # For now, return common languages
    return {
        "languages": [
            {"code": "eng", "name": "English"},
            {"code": "spa", "name": "Spanish"},
            {"code": "fra", "name": "French"},
            {"code": "deu", "name": "German"},
            {"code": "ita", "name": "Italian"},
            {"code": "por", "name": "Portuguese"},
            {"code": "rus", "name": "Russian"},
            {"code": "ara", "name": "Arabic"},
            {"code": "chi_sim", "name": "Chinese (Simplified)"},
            {"code": "jpn", "name": "Japanese"},
        ],
        "default": settings.TESSERACT_LANG
    }

@app.post("/api/ocr")
async def process_ocr(file: UploadFile = File(...)) -> Dict:
    """
    Process uploaded file and extract text using OCR
    
    Args:
        file: Uploaded image or PDF file
    
    Returns:
        JSON response with extracted text and metadata
    """
    temp_file_path = None
    
    try:
        # Validate uploaded file
        logger.info(f"Received file: {file.filename}")
        safe_filename, file_extension = FileValidator.validate_upload(file)
        
        # Generate unique filename to avoid collisions
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        temp_file_path = os.path.join(settings.TEMP_DIR, unique_filename)
        
        # Save uploaded file to temporary location
        logger.info(f"Saving file to: {temp_file_path}")
        async with aiofiles.open(temp_file_path, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)
        
        # Process file with OCR
        logger.info(f"Processing file with OCR: {safe_filename}")
        result = ocr_processor.process_file(temp_file_path, file_extension)
        
        # Check if processing was successful
        if not result.get("success", False):
            raise HTTPException(
                status_code=500,
                detail=f"OCR processing failed: {result.get('error', 'Unknown error')}"
            )
        
        # Add original filename to response
        result["original_filename"] = safe_filename
        
        logger.info(f"OCR completed successfully. Extracted {result.get('word_count', 0)} words")
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data": result,
                "message": "Text extracted successfully"
            }
        )
        
    except HTTPException as he:
        # Re-raise HTTP exceptions
        logger.error(f"HTTP error: {he.detail}")
        raise he
        
    except Exception as e:
        # Handle unexpected errors
        logger.error(f"Unexpected error during OCR processing: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred during processing: {str(e)}"
        )
        
    finally:
        # Clean up temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
                logger.info(f"Cleaned up temporary file: {temp_file_path}")
            except Exception as e:
                logger.error(f"Failed to clean up temporary file: {str(e)}")

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "status_code": exc.status_code
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "An internal server error occurred",
            "status_code": 500
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
