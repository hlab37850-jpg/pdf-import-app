import json
import time
import os
from typing import Dict, Any, List

# Import the PDF engine
from engine.orchestrator import PDFImportOrchestrator

class PDFProcessingResult:
    def __init__(self):
        self.text = ""
        self.confidence = 0.0
        self.pages_processed = 0
        self.tables_extracted = 0
        self.images_extracted = 0
        self.processing_time = 0
        self.extraction_method = "unknown"
        self.languages = []
        self.metadata = {}
        self.warnings = []
        self.errors = []
    
    def to_json(self) -> str:
        return json.dumps({
            "text": self.text,
            "confidence": self.confidence,
            "pages_processed": self.pages_processed,
            "tables_extracted": self.tables_extracted,
            "images_extracted": self.images_extracted,
            "processing_time": self.processing_time,
            "extraction_method": self.extraction_method,
            "languages": self.languages,
            "metadata": self.metadata,
            "warnings": self.warnings,
            "errors": self.errors
        }, ensure_ascii=False)

def process_pdf(pdf_path: str) -> PDFProcessingResult:
    """Main entry point for PDF processing"""
    result = PDFProcessingResult()
    
    try:
        start_time = time.time()
        
        # Initialize the orchestrator
        orchestrator = PDFImportOrchestrator()
        
        # Process the PDF
        processing_result = orchestrator.process(pdf_path)
        
        # Fill result object
        result.text = processing_result.get('text', '')
        result.confidence = processing_result.get('confidence', 0.0)
        result.pages_processed = processing_result.get('pages_processed', 0)
        result.tables_extracted = processing_result.get('tables_extracted', 0)
        result.images_extracted = processing_result.get('images_extracted', 0)
        result.extraction_method = processing_result.get('method', 'unknown')
        result.languages = processing_result.get('languages', [])
        result.metadata = processing_result.get('metadata', {})
        result.warnings = processing_result.get('warnings', [])
        result.errors = processing_result.get('errors', [])
        
        result.processing_time = int((time.time() - start_time) * 1000)
        
    except Exception as e:
        result.errors.append(f"Processing error: {str(e)}")
        result.confidence = 0.0
    
    return result

# Keep reference to avoid garbage collection
_orchestrator = None

def initialize_engine():
    """Initialize the PDF processing engine"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = PDFImportOrchestrator()
    return _orchestrator

def get_engine_status() -> Dict[str, Any]:
    """Get current engine status"""
    return {
        "initialized": _orchestrator is not None,
        "version": "1.0.0",
        "supported_formats": ["pdf", "PDF"],
        "max_file_size_mb": 100,
        "features": [
            "text_extraction",
            "table_extraction",
            "image_extraction",
            "layout_analysis",
            "multi_language",
            "arabic_support"
        ]
    }
