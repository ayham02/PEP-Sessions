import os
import cv2
import numpy as np
import pytesseract
from PIL import Image
from pdf2image import convert_from_path
from typing import Dict, List, Optional
import tempfile
import logging
from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OCRProcessor:
    """Handles OCR processing with image preprocessing"""
    
    def __init__(self):
        self.tesseract_config = settings.TESSERACT_CONFIG
        self.language = settings.TESSERACT_LANG
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Apply preprocessing pipeline to enhance OCR accuracy
        
        Steps:
        1. Convert to grayscale
        2. Apply Gaussian blur to reduce noise
        3. Apply adaptive thresholding for better contrast
        4. Optional: Deskew if needed
        """
        # Convert to grayscale if not already
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Apply adaptive thresholding
        # This works better than simple thresholding for varying lighting conditions
        thresh = cv2.adaptiveThreshold(
            blurred,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11,
            2
        )
        
        # Optional: Apply morphological operations to remove noise
        kernel = np.ones((1, 1), np.uint8)
        processed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        processed = cv2.morphologyEx(processed, cv2.MORPH_OPEN, kernel)
        
        return processed
    
    def resize_image_if_needed(self, image: np.ndarray) -> np.ndarray:
        """Resize image if it exceeds maximum dimensions"""
        height, width = image.shape[:2]
        max_dim = settings.MAX_IMAGE_DIMENSION
        
        if height > max_dim or width > max_dim:
            # Calculate scaling factor
            scale = min(max_dim / height, max_dim / width)
            new_width = int(width * scale)
            new_height = int(height * scale)
            
            # Resize with high-quality interpolation
            resized = cv2.resize(
                image,
                (new_width, new_height),
                interpolation=cv2.INTER_CUBIC
            )
            logger.info(f"Resized image from {width}x{height} to {new_width}x{new_height}")
            return resized
        
        return image
    
    def extract_text_from_image(self, image_path: str) -> Dict:
        """
        Extract text from image file
        
        Returns:
            Dict with extracted text, confidence, and metadata
        """
        try:
            # Read image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError("Failed to load image")
            
            # Resize if needed
            image = self.resize_image_if_needed(image)
            
            # Preprocess image
            processed_image = self.preprocess_image(image)
            
            # Perform OCR with detailed data
            ocr_data = pytesseract.image_to_data(
                processed_image,
                lang=self.language,
                config=self.tesseract_config,
                output_type=pytesseract.Output.DICT
            )
            
            # Extract text
            text = pytesseract.image_to_string(
                processed_image,
                lang=self.language,
                config=self.tesseract_config
            )
            
            # Calculate average confidence
            confidences = [int(conf) for conf in ocr_data['conf'] if int(conf) > 0]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            # Count words
            words = [word for word in ocr_data['text'] if word.strip()]
            
            return {
                "text": text.strip(),
                "confidence": round(avg_confidence, 2),
                "word_count": len(words),
                "language": self.language,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error during OCR processing: {str(e)}")
            return {
                "text": "",
                "confidence": 0,
                "word_count": 0,
                "language": self.language,
                "success": False,
                "error": str(e)
            }
    
    def extract_text_from_pdf(self, pdf_path: str) -> Dict:
        """
        Extract text from PDF file by converting to images
        
        Returns:
            Dict with extracted text from all pages
        """
        try:
            # Convert PDF to images
            images = convert_from_path(pdf_path, dpi=settings.TARGET_DPI)
            
            all_text = []
            all_confidences = []
            total_words = 0
            
            # Process each page
            for i, image in enumerate(images):
                logger.info(f"Processing PDF page {i + 1}/{len(images)}")
                
                # Convert PIL Image to numpy array
                image_np = np.array(image)
                
                # Convert RGB to BGR for OpenCV
                if len(image_np.shape) == 3:
                    image_np = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
                
                # Resize if needed
                image_np = self.resize_image_if_needed(image_np)
                
                # Preprocess
                processed = self.preprocess_image(image_np)
                
                # Extract text
                page_text = pytesseract.image_to_string(
                    processed,
                    lang=self.language,
                    config=self.tesseract_config
                )
                
                # Get confidence data
                ocr_data = pytesseract.image_to_data(
                    processed,
                    lang=self.language,
                    config=self.tesseract_config,
                    output_type=pytesseract.Output.DICT
                )
                
                confidences = [int(conf) for conf in ocr_data['conf'] if int(conf) > 0]
                if confidences:
                    all_confidences.extend(confidences)
                
                words = [word for word in ocr_data['text'] if word.strip()]
                total_words += len(words)
                
                all_text.append(f"--- Page {i + 1} ---\n{page_text.strip()}")
            
            # Combine all pages
            combined_text = "\n\n".join(all_text)
            
            # Calculate average confidence
            avg_confidence = sum(all_confidences) / len(all_confidences) if all_confidences else 0
            
            return {
                "text": combined_text,
                "confidence": round(avg_confidence, 2),
                "word_count": total_words,
                "page_count": len(images),
                "language": self.language,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error during PDF OCR processing: {str(e)}")
            return {
                "text": "",
                "confidence": 0,
                "word_count": 0,
                "page_count": 0,
                "language": self.language,
                "success": False,
                "error": str(e)
            }
    
    def process_file(self, file_path: str, file_extension: str) -> Dict:
        """
        Process file based on extension
        
        Args:
            file_path: Path to the file
            file_extension: File extension (.pdf, .png, etc.)
        
        Returns:
            Dict with OCR results
        """
        if file_extension.lower() == '.pdf':
            return self.extract_text_from_pdf(file_path)
        else:
            return self.extract_text_from_image(file_path)
