"""
Text Processor
Process and clean extracted text
"""

import re
from typing import List


class TextProcessor:
    """Process and clean text"""
    
    def __init__(self):
        self.method_name = "text_processor"
    
    def process(self, text: str) -> str:
        """Process and clean text"""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r' {2,}', ' ', text)
        
        # Remove control characters
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
        
        return text.strip()
    
    def extract_paragraphs(self, text: str) -> List[str]:
        """Extract paragraphs from text"""
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        return paragraphs
    
    def extract_headings(self, text: str) -> List[str]:
        """Extract potential headings"""
        headings = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if line and len(line) < 100 and not line.endswith('.'):
                # Check if line looks like a heading
                if line.isupper() or (len(line) < 50 and line[0].isupper()):
                    headings.append(line)
        
        return headings
