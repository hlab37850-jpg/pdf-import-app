"""
Language Detector
Detect language of extracted text
"""

from typing import List, Dict, Any


class LanguageDetector:
    """Detect languages in text"""
    
    def __init__(self):
        self.method_name = "language_detector"
    
    def detect(self, text: str) -> List[Dict[str, Any]]:
        """Detect languages in text"""
        languages = []
        
        try:
            from langdetect import detect_langs
            
            # Detect on first 1000 characters
            sample = text[:1000]
            detected = detect_langs(sample)
            
            for lang in detected:
                languages.append({
                    'language': lang.lang,
                    'probability': lang.prob
                })
            
        except ImportError:
            pass
        except Exception:
            pass
        
        return languages
    
    def detect_simple(self, text: str) -> str:
        """Simple language detection"""
        try:
            from langdetect import detect
            return detect(text[:1000])
        except:
            return "unknown"
    
    def is_arabic(self, text: str) -> bool:
        """Check if text contains Arabic characters"""
        arabic_chars = set('ابتثجحخدذرزسشصضطظعغفقكلمنهوي')
        text_chars = set(text[:1000])
        return len(text_chars.intersection(arabic_chars)) > 0
