"""
PDF Analyzer
Analyze PDF structure and content
"""

from typing import Dict, Any
import os


class PDFAnalyzer:
    """Analyze PDF files"""
    
    def __init__(self):
        self.method_name = "pdf_analyzer"
    
    def analyze(self, pdf_path: str) -> Dict[str, Any]:
        """Analyze PDF file"""
        result = {
            'file_size': 0,
            'is_valid': False,
            'has_text': False,
            'has_images': False,
            'is_scanned': False,
            'page_count': 0,
            'error': None
        }
        
        try:
            # File size
            result['file_size'] = os.path.getsize(pdf_path)
            
            # Check if valid PDF
            with open(pdf_path, 'rb') as f:
                magic = f.read(4)
                result['is_valid'] = (magic == b'%PDF')
            
            if not result['is_valid']:
                return result
            
            # Try PyMuPDF analysis
            try:
                import fitz
                doc = fitz.open(pdf_path)
                
                result['page_count'] = len(doc)
                
                total_text = 0
                total_images = 0
                
                for page in doc:
                    text = page.get_text()
                    total_text += len(text.strip())
                    
                    images = page.get_images()
                    total_images += len(images)
                
                result['has_text'] = total_text > 100
                result['has_images'] = total_images > 0
                result['is_scanned'] = total_images > 0 and total_text < 100
                
                doc.close()
                
            except ImportError:
                result['error'] = "PyMuPDF not available"
            
        except Exception as e:
            result['error'] = str(e)
        
        return result
