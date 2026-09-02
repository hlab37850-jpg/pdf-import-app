"""
Basic tests for PDF Import Orchestrator
"""

import sys
import os
import pytest

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from core.orchestrator import PDFImportOrchestrator
    ORCHESTRATOR_AVAILABLE = True
except ImportError:
    ORCHESTRATOR_AVAILABLE = False


@pytest.mark.skipif(not ORCHESTRATOR_AVAILABLE, reason="Orchestrator not available")
class TestPDFImportOrchestrator:
    
    def test_init(self):
        orchestrator = PDFImportOrchestrator()
        assert orchestrator is not None
    
    def test_validate_pdf(self):
        orchestrator = PDFImportOrchestrator()
        
        # Test with non-existent file
        result = orchestrator.process("/nonexistent/file.pdf")
        assert result['confidence'] == 0.0
        assert 'errors' in result
    
    def test_process_invalid_file(self):
        orchestrator = PDFImportOrchestrator()
        
        # Create a fake PDF file
        fake_pdf = "/tmp/fake.pdf"
        with open(fake_pdf, 'w') as f:
            f.write("This is not a PDF")
        
        result = orchestrator.process(fake_pdf)
        assert result['confidence'] == 0.0
        assert 'errors' in result
