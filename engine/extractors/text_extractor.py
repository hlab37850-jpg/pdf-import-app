"""
Text Extractor
Basic text extraction from PDF
"""

from typing import Dict, Any


class TextExtractor:
    """Extract text from PDF files"""
    
    def __init__(self):
        self.method_name = "text_extractor"
    
    def extract(self, pdf_path: str) -> Dict[str, Any]:
        """Extract text from PDF"""
        result = {
            'text': '',
            'success': False,
            'error': None
        }
        
        try:
            import fitz
            doc = fitz.open(pdf_path)
            
            text_parts = []
            for page in doc:
                text_parts.append(page.get_text())
            
            doc.close()
            
            result['text'] = '\n\n'.join(text_parts)
            result['success'] = True
            
        except ImportError:
            result['error'] = "PyMuPDF not available"
        except Exception as e:
            result['error'] = str(e)
        
        return result
