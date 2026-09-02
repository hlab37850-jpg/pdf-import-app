"""
Arabic Processor
Process Arabic text for proper display
"""


class ArabicProcessor:
    """Process Arabic text"""
    
    def __init__(self):
        self.method_name = "arabic_processor"
    
    def process(self, text: str) -> str:
        """Process Arabic text for proper display"""
        if not text:
            return ""
        
        try:
            import arabic_reshaper
            from bidi.algorithm import get_display
            
            reshaped_text = arabic_reshaper.reshape(text)
            bidi_text = get_display(reshaped_text)
            return bidi_text
            
        except ImportError:
            return text
        except Exception:
            return text
    
    def is_arabic_text(self, text: str) -> bool:
        """Check if text contains Arabic"""
        arabic_chars = set('ابتثجحخدذرزسشصضطظعغفقكلمنهوي')
        text_chars = set(text[:1000])
        return len(text_chars.intersection(arabic_chars)) > 0
