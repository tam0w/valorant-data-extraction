import logging
import sys
import random
import string
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
import cv2
import numpy as np


class Logger:
    """
    Functional logger module that stores screenshots and logs
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance._init()
        return cls._instance

    def _init(self):
        # Initialize logger
        self.logger = logging.getLogger("PractisticsLogger")
        self.logger.setLevel(logging.DEBUG)

        # Create formatter
        self.formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # Console handler
        self.console_handler = logging.StreamHandler(sys.stdout)
        self.console_handler.setFormatter(self.formatter)
        self.console_handler.setLevel(logging.INFO)
        self.logger.addHandler(self.console_handler)

        # File handler will be created on demand
        self.file_handler = None

        # Image storage
        self.scoreboard_image = None
        self.summary_image = None
        self.timeline_images = []
        self.error_id = None

    def store_scoreboard(self, image: np.ndarray):
        self.scoreboard_image = image.copy()
        self.debug("Stored scoreboard image")

    def store_summary(self, image: np.ndarray):
        self.summary_image = image.copy()
        self.debug("Stored summary image")

    def store_timeline(self, image: np.ndarray):
        self.timeline_images.append(image.copy())
        self.debug(f"Stored timeline image #{len(self.timeline_images)}")

    def debug(self, message: str):
        self.logger.debug(message)

    def info(self, message: str):
        self.logger.info(message)

    def warning(self, message: str):
        self.logger.warning(message)

    def error(self, message: str):
        self.logger.error(message)

    def _generate_error_id(self) -> str:
        return 'E' + ''.join(random.choices(string.digits, k=7))

    def _setup_file_logging(self, config: Dict[str, Any]) -> Path:
        # Generate error ID if not exists
        if not self.error_id:
            self.error_id = self._generate_error_id()

        log_dir = Path(config['log_dir']) / self.error_id
        log_dir.mkdir(parents=True, exist_ok=True)

        # Create log file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"log_{timestamp}.txt"

        # Create and setup file handler
        self.file_handler = logging.FileHandler(log_file)
        self.file_handler.setFormatter(self.formatter)
        self.file_handler.setLevel(logging.DEBUG)
        self.logger.addHandler(self.file_handler)

        self.debug(f"Log directory: {log_dir}")

        return log_dir

    def save_logs(self, config: Dict[str, Any], exception_info: Optional[str] = None) -> str:
        log_dir = self._setup_file_logging(config)

        if exception_info:
            self.error(f"Exception Information: {exception_info}")

        # Save scoreboard image
        if self.scoreboard_image is not None:
            image_path = log_dir / "scoreboard.png"
            cv2.imwrite(str(image_path), self.scoreboard_image)
            self.info("Saved scoreboard image")

        # Save summary image
        if self.summary_image is not None:
            image_path = log_dir / "summary.png"
            cv2.imwrite(str(image_path), self.summary_image)
            self.info("Saved summary image")

        # Save timeline images
        for idx, image in enumerate(self.timeline_images, 1):
            image_path = log_dir / f"timeline_{idx}.png"
            cv2.imwrite(str(image_path), image)
            self.info(f"Saved timeline image #{idx}")

        # Clean up file handler
        if self.file_handler:
            self.logger.removeHandler(self.file_handler)
            self.file_handler.close()
            self.file_handler = None

        return self.error_id


# Create singleton instance
logger = Logger()