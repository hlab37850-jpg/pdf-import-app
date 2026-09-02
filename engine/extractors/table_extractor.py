"""
Table Extractor
Extract tables from PDF files using multiple methods
"""

from typing import Dict, Any, List


class TableExtractor:
    """Extract tables from PDF files"""
    
    def __init__(self):
        self.method_name = "table_extractor"
    
    def extract(self, pdf_path: str) -> Dict[str, Any]:
        """Extract tables from PDF"""
        result = {
            'tables': [],
            'success': False,
            'error': None
        }
        
        # Try PyMuPDF first
        try:
            import fitz
            doc = fitz.open(pdf_path)
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                tables = self._detect_tables_pymupdf(page)
                result['tables'].extend(tables)
            
            doc.close()
            result['success'] = True
            
        except ImportError:
            # Try pdfminer
            try:
                tables = self._detect_tables_pdfminer(pdf_path)
                result['tables'].extend(tables)
                result['success'] = True
            except Exception as e:
                result['error'] = f"pdfminer failed: {str(e)}"
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def _detect_tables_pymupdf(self, page) -> List[Dict[str, Any]]:
        """Detect tables using PyMuPDF"""
        tables = []
        try:
            blocks = page.get_text("dict")["blocks"]
            
            for block in blocks:
                if block.get("type") == 0:
                    lines = block.get("lines", [])
                    if len(lines) >= 2:
                        x_coords = []
                        for line in lines:
                            for span in line.get("spans", []):
                                x_coords.append(span.get("bbox", [0,0,0,0])[0])
                        
                        if len(set(x_coords)) >= 3:
                            tables.append({
                                "page": page.number + 1,
                                "bbox": block.get("bbox", [0,0,0,0]),
                                "rows": len(lines),
                                "columns": len(set(x_coords))
                            })
        except:
            pass
        
        return tables
    
    def _detect_tables_pdfminer(self, pdf_path: str) -> List[Dict[str, Any]]:
        """Detect tables using pdfminer"""
        tables = []
        try:
            from pdfminer.pdfparser import PDFParser
            from pdfminer.pdfdocument import PDFDocument
            from pdfminer.pdfpage import PDFPage
            from pdfminer.layout import LAParams
            from pdfminer.converter import PDFPageAggregator
            from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
            
            with open(pdf_path, 'rb') as f:
                parser = PDFParser(f)
                document = PDFDocument(parser)
                rsrcmgr = PDFResourceManager()
                laparams = LAParams()
                device = PDFPageAggregator(rsrcmgr, laparams=laparams)
                interpreter = PDFPageInterpreter(rsrcmgr, device)
                
                for page_num, page in enumerate(PDFPage.create_pages(document)):
                    interpreter.process_page(page)
                    layout = device.get_result()
                    
                    for element in layout:
                        if hasattr(element, 'items') and len(element.items) >= 3:
                            tables.append({
                                "page": page_num + 1,
                                "bbox": getattr(element, 'bbox', [0,0,0,0]),
                                "items": len(element.items)
                            })
        except:
            pass
        
        return tables
