"""
Extraction Strategy
Strategy pattern for different extraction methods
"""

from typing import Dict, Any, List
from abc import ABC, abstractmethod


class ExtractionStrategy(ABC):
    """Abstract base class for extraction strategies"""
    
    @abstractmethod
    def extract(self, pdf_path: str) -> Dict[str, Any]:
        """Extract content from PDF"""
        pass
    
    @abstractmethod
    def can_handle(self, pdf_info: Dict[str, Any]) -> bool:
        """Check if strategy can handle the PDF"""
        pass


class TextExtractionStrategy(ExtractionStrategy):
    """Strategy for text-based PDFs"""
    
    def extract(self, pdf_path: str) -> Dict[str, Any]:
        result = {'text': '', 'method': 'text'}
        # Text extraction logic
        return result
    
    def can_handle(self, pdf_info: Dict[str, Any]) -> bool:
        return pdf_info.get('has_text', False)


class OCRExtractionStrategy(ExtractionStrategy):
    """Strategy for scanned PDFs"""
    
    def extract(self, pdf_path: str) -> Dict[str, Any]:
        result = {'text': '', 'method': 'ocr'}
        # OCR logic
        return result
    
    def can_handle(self, pdf_info: Dict[str, Any]) -> bool:
        return pdf_info.get('is_scanned', False)
