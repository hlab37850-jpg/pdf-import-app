"""
Image Extractor
Extract images from PDF files using multiple methods
"""

from typing import Dict, Any, List


class ImageExtractor:
    """Extract images from PDF files"""
    
    def __init__(self):
        self.method_name = "image_extractor"
    
    def extract(self, pdf_path: str) -> Dict[str, Any]:
        """Extract images from PDF"""
        result = {
            'images': [],
            'count': 0,
            'success': False,
            'error': None
        }
        
        # Try PyMuPDF first
        try:
            import fitz
            doc = fitz.open(pdf_path)
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                images = page.get_images()
                
                for img in images:
                    result['images'].append({
                        'page': page_num + 1,
                        'xref': img[0],
                        'width': img[2] if len(img) > 2 else 0,
                        'height': img[3] if len(img) > 3 else 0
                    })
                    result['count'] += 1
            
            doc.close()
            result['success'] = True
            
        except ImportError:
            result['error'] = "PyMuPDF not available for image extraction"
        except Exception as e:
            result['error'] = str(e)
        
        return result
