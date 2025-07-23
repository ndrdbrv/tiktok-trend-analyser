"""
OCR Processing Component
=======================

Handles thumbnail text extraction using Tesseract OCR.
"""

import requests
from PIL import Image
from io import BytesIO
import pytesseract
from typing import Dict, Optional

class OCRProcessor:
    """Handles OCR text extraction from thumbnails"""
    
    def __init__(self):
        self.timeout = 15
        
    def extract_thumbnail_text(self, thumbnail_url: str) -> Optional[Dict[str, str]]:
        """Extract text from thumbnail image"""
        
        if not thumbnail_url:
            return None
            
        try:
            # Download thumbnail
            response = requests.get(thumbnail_url, timeout=self.timeout)
            response.raise_for_status()
            
            # Load image
            image = Image.open(BytesIO(response.content))
            
            # Extract text with OCR
            raw_text = pytesseract.image_to_string(image)
            
            # Clean text
            cleaned_text = self._clean_ocr_text(raw_text)
            
            return {
                'raw_text': raw_text,
                'cleaned_text': cleaned_text,
                'confidence': 'High' if cleaned_text.strip() else 'Low'
            }
            
        except Exception as e:
            return {
                'raw_text': '',
                'cleaned_text': f'OCR failed: {str(e)[:30]}',
                'confidence': 'Failed'
            }
    
    def _clean_ocr_text(self, text: str) -> str:
        """Clean and format OCR text"""
        
        if not text:
            return ""
        
        lines = text.strip().split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if len(line) >= 2:  # Filter out single characters
                # Filter out common OCR artifacts
                if not line.isdigit() and not line in ['|', '-', '_', '.', ',']:
                    # Fix common OCR mistakes
                    line = line.replace('|', 'I')
                    line = line.replace('0', 'O')
                    cleaned_lines.append(line)
        
        return ' '.join(cleaned_lines)
    
    def process_videos_batch(self, videos: list) -> list:
        """Process OCR for a batch of videos"""
        
        for i, video in enumerate(videos):
            print(f"🔍 Processing OCR {i+1}/{len(videos)}: @{video.get('author', 'unknown')}")
            
            ocr_result = self.extract_thumbnail_text(video.get('thumbnail_url', ''))
            
            if ocr_result:
                video['ocr_text'] = ocr_result['cleaned_text']
                video['ocr_confidence'] = ocr_result['confidence']
            else:
                video['ocr_text'] = 'No text found'
                video['ocr_confidence'] = 'Low'
        
        return videos 