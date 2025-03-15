import easyocr
import numpy as np
import time
from typing import List, Dict, Any, Optional, Tuple
from core.logger import logger

# Global reader instance
reader = None


def initialize_ocr(lang: List[str] = ['en'], download_enabled: bool = True):
    """Initialize the OCR reader"""
    global reader

    logger.push_context(operation="initialize_ocr")

    start_time = time.time()
    logger.debug(f"Initializing OCR with languages: {lang}")

    try:
        reader = easyocr.Reader(lang, download_enabled=download_enabled)
        elapsed_time = time.time() - start_time
        logger.debug(f"OCR initialization completed in {elapsed_time:.2f} seconds")
    except Exception as e:
        logger.error(f"Failed to initialize OCR: {str(e)}")
        raise
    finally:
        logger.clear_context()

    return reader


def extract_text(image: np.ndarray, detail: int = 0, region_name: str = "unnamed", **kwargs) -> List[str]:
    """
    Extract text from image with options

    Args:
        image: The image to extract text from
        detail: The level of detail to return (0 for text only, 1 for text and bounding boxes)
        region_name: A descriptive name for the image region (for better logging)
        **kwargs: Additional kwargs passed to EasyOCR

    Returns:
        List of extracted text strings
    """
    global reader
    if reader is None:
        logger.debug("OCR reader not initialized, initializing now")
        initialize_ocr()

    logger.push_context(operation="ocr", region=region_name)

    try:
        image_shape = image.shape
        logger.debug(f"Extracting text from {region_name} region "
                     f"(shape: {image_shape}, detail: {detail}, kwargs: {kwargs})")

        start_time = time.time()
        result = reader.readtext(image, detail=detail, **kwargs)
        elapsed_time = time.time() - start_time

        if detail == 0:
            # Only text strings in result
            text_count = len(result)
            logger.debug(
                f"Extracted {text_count} text items in {elapsed_time:.2f}s: {result[:3]}{'...' if text_count > 3 else ''}")
        else:
            # Results include bounding boxes
            text_count = len(result)
            texts = [item[1] for item in result]
            logger.debug(
                f"Extracted {text_count} text items in {elapsed_time:.2f}s: {texts[:3]}{'...' if text_count > 3 else ''}")

        if text_count == 0:
            logger.warning(f"No text detected in {region_name} region")

        return result

    except Exception as e:
        logger.error(f"OCR extraction failed for {region_name} region: {str(e)}")
        return []
    finally:
        logger.clear_context()


def extract_numeric_value(image: np.ndarray, region_name: str = "numeric") -> int:
    """
    Extract numeric value from image

    Args:
        image: The image containing a numeric value
        region_name: A descriptive name for the image region (for better logging)

    Returns:
        The extracted integer value, or 0 if extraction fails
    """
    global reader
    if reader is None:
        initialize_ocr()

    logger.push_context(operation="ocr_numeric", region=region_name)

    try:
        logger.debug(f"Extracting numeric value from {region_name} region")

        start_time = time.time()
        result = reader.readtext(
            image,
            allowlist='0123456789',
            detail=0
        )
        elapsed_time = time.time() - start_time

        if result and len(result) > 0:
            try:
                value = int(result[0])
                logger.debug(f"Extracted numeric value: {value} in {elapsed_time:.2f}s")
                return value
            except ValueError:
                logger.warning(f"Failed to convert extracted value '{result[0]}' to integer")
                return 0
        else:
            logger.warning(f"No numeric value detected in {region_name} region")
            return 0

    except Exception as e:
        logger.error(f"Numeric OCR extraction failed for {region_name} region: {str(e)}")
        return 0
    finally:
        logger.clear_context()