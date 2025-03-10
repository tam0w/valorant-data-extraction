import easyocr
import numpy as np
from typing import List, Dict, Any, Optional


# Initialize OCR reader
def initialize_ocr(lang: List[str] = ['en'], download_enabled: bool = True):
    """Initialize the OCR reader"""
    global reader
    reader = easyocr.Reader(lang, download_enabled=download_enabled)
    return reader


# Global reader instance
reader = None


def extract_text(image: np.ndarray, detail: int = 0, **kwargs) -> List[str]:
    """Extract text from image with options"""
    global reader
    if reader is None:
        initialize_ocr()

    return reader.readtext(image, detail=detail, **kwargs)


def extract_numeric_value(image: np.ndarray) -> int:
    """Extract numeric value from image"""
    global reader
    if reader is None:
        initialize_ocr()

    result = reader.readtext(
        image,
        allowlist='0123456789',
        detail=0
    )

    if result and len(result) > 0:
        try:
            return int(result[0])
        except ValueError:
            return 0
    return 0