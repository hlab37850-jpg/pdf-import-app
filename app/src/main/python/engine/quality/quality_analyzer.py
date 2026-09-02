"""
Quality Analyzer
Analyze quality of extraction results
"""

from typing import Dict, Any


class QualityAnalyzer:
    """Analyze extraction quality"""
    
    def __init__(self):
        self.method_name = "quality_analyzer"
    
    def analyze(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze quality of extraction"""
        quality = {
            'confidence': 0.0,
            'text_quality': 0.0,
            'completeness': 0.0,
            'issues': []
        }
        
        text = result.get('text', '')
        
        # Text quality
        text_length = len(text)
        if text_length > 1000:
            quality['text_quality'] = 0.9
        elif text_length > 500:
            quality['text_quality'] = 0.7
        elif text_length > 100:
            quality['text_quality'] = 0.5
        elif text_length > 0:
            quality['text_quality'] = 0.3
            quality['issues'].append("Very little text extracted")
        else:
            quality['text_quality'] = 0.0
            quality['issues'].append("No text extracted")
        
        # Completeness
        if result.get('tables_extracted', 0) > 0:
            quality['completeness'] += 0.2
        
        if result.get('images_extracted', 0) > 0:
            quality['completeness'] += 0.1
        
        # Calculate overall confidence
        quality['confidence'] = (quality['text_quality'] * 0.7 + quality['completeness'] * 0.3)
        
        # Cap at 0.95
        quality['confidence'] = min(quality['confidence'], 0.95)
        
        return quality
