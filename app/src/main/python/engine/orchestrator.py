"""
PDF Import Orchestrator
Main orchestration logic for PDF processing
"""

import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

try:
    from pdfminer.high_level import extract_text as pdfminer_extract
    PDFMINER_AVAILABLE = True
except ImportError:
    PDFMINER_AVAILABLE = False

try:
    from langdetect import detect, detect_langs
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False

try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    ARABIC_SUPPORT_AVAILABLE = True
except ImportError:
    ARABIC_SUPPORT_AVAILABLE = False


class PDFImportOrchestrator:
    """Main orchestrator for PDF import and processing"""
    
    def __init__(self):
        self.extraction_methods = []
        self._register_available_methods()
    
    def _register_available_methods(self):
        """Register available extraction methods"""
        if PYMUPDF_AVAILABLE:
            self.extraction_methods.append('pymupdf')
        if PDFPLUMBER_AVAILABLE:
            self.extraction_methods.append('pdfplumber')
        if PDFMINER_AVAILABLE:
            self.extraction_methods.append('pdfminer')
        
        if not self.extraction_methods:
            self.extraction_methods.append('basic')
    
    def process(self, pdf_path: str) -> Dict[str, Any]:
        """Process a PDF file and extract content"""
        result = {
            'text': '',
            'confidence': 0.0,
            'pages_processed': 0,
            'tables_extracted': 0,
            'images_extracted': 0,
            'method': 'unknown',
            'languages': [],
            'metadata': {},
            'warnings': [],
            'errors': []
        }
        
        if not os.path.exists(pdf_path):
            result['errors'].append(f"File not found: {pdf_path}")
            return result
        
        # Validate PDF file
        if not self._is_valid_pdf(pdf_path):
            result['errors'].append("Invalid PDF file")
            return result
        
        # Try extraction methods in order
        for method in self.extraction_methods:
            try:
                extracted = self._extract_with_method(pdf_path, method)
                
                if extracted and extracted.get('text'):
                    result.update(extracted)
                    result['method'] = method
                    result['confidence'] = self._calculate_confidence(extracted)
                    
                    # Detect languages
                    if LANGDETECT_AVAILABLE and extracted.get('text'):
                        try:
                            detected_langs = detect_langs(extracted['text'][:1000])
                            result['languages'] = [str(lang).split(':')[0] for lang in detected_langs]
                        except:
                            pass
                    
                    # Process Arabic text if needed
                    if ARABIC_SUPPORT_AVAILABLE and 'ar' in result.get('languages', []):
                        result['text'] = self._process_arabic_text(result['text'])
                    
                    break
            except Exception as e:
                result['warnings'].append(f"{method} failed: {str(e)}")
        
        # If no text extracted, try basic method
        if not result.get('text'):
            try:
                basic_text = self._basic_extraction(pdf_path)
                if basic_text:
                    result['text'] = basic_text
                    result['method'] = 'basic'
                    result['confidence'] = 0.3
            except Exception as e:
                result['errors'].append(f"Basic extraction failed: {str(e)}")
        
        # Extract metadata
        result['metadata'] = self._extract_metadata(pdf_path)
        
        # Count pages
        result['pages_processed'] = self._count_pages(pdf_path)
        
        return result
    
    def _is_valid_pdf(self, pdf_path: str) -> bool:
        """Check if file is a valid PDF"""
        try:
            with open(pdf_path, 'rb') as f:
                magic = f.read(4)
                return magic == b'%PDF'
        except:
            return False
    
    def _extract_with_method(self, pdf_path: str, method: str) -> Optional[Dict[str, Any]]:
        """Extract text using specified method"""
        if method == 'pymupdf' and PYMUPDF_AVAILABLE:
            return self._extract_pymupdf(pdf_path)
        elif method == 'pdfplumber' and PDFPLUMBER_AVAILABLE:
            return self._extract_pdfplumber(pdf_path)
        elif method == 'pdfminer' and PDFMINER_AVAILABLE:
            return self._extract_pdfminer(pdf_path)
        return None
    
    def _extract_pymupdf(self, pdf_path: str) -> Dict[str, Any]:
        """Extract using PyMuPDF"""
        result = {'text': '', 'tables_extracted': 0, 'images_extracted': 0}
        
        doc = fitz.open(pdf_path)
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            
            # Extract text
            text = page.get_text()
            result['text'] += text + "\n\n"
            
            # Count images
            images = page.get_images()
            result['images_extracted'] += len(images)
        
        doc.close()
        return result
    
    def _extract_pdfplumber(self, pdf_path: str) -> Dict[str, Any]:
        """Extract using pdfplumber"""
        result = {'text': '', 'tables_extracted': 0, 'images_extracted': 0}
        
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                # Extract text
                text = page.extract_text()
                if text:
                    result['text'] += text + "\n\n"
                
                # Extract tables
                tables = page.extract_tables()
                result['tables_extracted'] += len(tables)
                
                # Count images
                if hasattr(page, 'images'):
                    result['images_extracted'] += len(page.images)
        
        return result
    
    def _extract_pdfminer(self, pdf_path: str) -> Dict[str, Any]:
        """Extract using pdfminer"""
        result = {'text': '', 'tables_extracted': 0, 'images_extracted': 0}
        
        text = pdfminer_extract(pdf_path)
        result['text'] = text
        
        return result
    
    def _basic_extraction(self, pdf_path: str) -> str:
        """Basic text extraction from raw PDF"""
        text = ""
        try:
            with open(pdf_path, 'rb') as f:
                content = f.read()
                
                # Try to find text streams
                text_blocks = []
                in_text = False
                current_text = []
                
                for i in range(len(content) - 1):
                    if content[i:i+2] == b'BT':
                        in_text = True
                        current_text = []
                    elif content[i:i+2] == b'ET':
                        in_text = False
                        if current_text:
                            text_blocks.append(b''.join(current_text))
                    elif in_text and content[i:i+2] == b'Tj':
                        # Extract text from Tj operator
                        start = max(0, i - 100)
                        chunk = content[start:i]
                        # Find text in parentheses
                        if b'(' in chunk:
                            text_start = chunk.rfind(b'(') + 1
                            text_end = chunk.find(b')', text_start)
                            if text_end > text_start:
                                text_bytes = chunk[text_start:text_end]
                                try:
                                    current_text.append(text_bytes)
                                except:
                                    pass
                
                if text_blocks:
                    text = '\n'.join(block.decode('utf-8', errors='ignore') for block in text_blocks)
        except:
            pass
        
        return text
    
    def _calculate_confidence(self, extracted: Dict[str, Any]) -> float:
        """Calculate confidence score based on extraction quality"""
        confidence = 0.5  # Base confidence
        
        text = extracted.get('text', '')
        
        # More text = higher confidence
        if len(text) > 1000:
            confidence += 0.2
        elif len(text) > 500:
            confidence += 0.1
        elif len(text) > 100:
            confidence += 0.05
        
        # Tables found
        if extracted.get('tables_extracted', 0) > 0:
            confidence += 0.1
        
        # Images found
        if extracted.get('images_extracted', 0) > 0:
            confidence += 0.05
        
        # Cap at 0.95
        return min(confidence, 0.95)
    
    def _process_arabic_text(self, text: str) -> str:
        """Process Arabic text for proper display"""
        try:
            reshaped_text = arabic_reshaper.reshape(text)
            bidi_text = get_display(reshaped_text)
            return bidi_text
        except:
            return text
    
    def _extract_metadata(self, pdf_path: str) -> Dict[str, str]:
        """Extract PDF metadata"""
        metadata = {}
        
        try:
            if PYMUPDF_AVAILABLE:
                doc = fitz.open(pdf_path)
                metadata = doc.metadata
                doc.close()
            elif PDFPLUMBER_AVAILABLE:
                with pdfplumber.open(pdf_path) as pdf:
                    metadata = pdf.metadata
        except:
            pass
        
        # Add file info
        metadata['file_size'] = str(os.path.getsize(pdf_path))
        metadata['file_name'] = os.path.basename(pdf_path)
        
        return metadata
    
    def _count_pages(self, pdf_path: str) -> int:
        """Count pages in PDF"""
        try:
            if PYMUPDF_AVAILABLE:
                doc = fitz.open(pdf_path)
                pages = len(doc)
                doc.close()
                return pages
            elif PDFPLUMBER_AVAILABLE:
                with pdfplumber.open(pdf_path) as pdf:
                    return len(pdf.pages)
        except:
            pass
        
        return 0
