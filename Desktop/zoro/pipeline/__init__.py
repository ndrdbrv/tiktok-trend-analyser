"""
TikTok Analysis Pipeline
=======================

Clean, modular pipeline for TikTok trending analysis.
Each component has a single responsibility.
"""

from .scraper import TikTokScraper
from .ocr_processor import OCRProcessor  
# LLMAnalyzer imported lazily to avoid early Claude initialization
from .metrics import MetricsCalculator
from .storage import DataStorage

__all__ = [
    'TikTokScraper',
    'OCRProcessor', 
    # 'LLMAnalyzer',  # Available via direct import only
    'MetricsCalculator',
    'DataStorage'
] 