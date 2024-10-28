import logging
import os
import sys
import random
import string
from datetime import datetime
from pathlib import Path
from typing import Optional, List
import cv2
import numpy as np


class Logger:

    """
    Custom logger that logs basic messages to terminal and saves detailed logs to a file. Also logs the all the
    screenshots taken so far to the error directory.
    """

    def __init__(self, name: str = "PractisticsLogger"):
        # Initialize logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)  # Capture all logs

        # Create formatter for consistent log formatting
        self.formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # Setup console handler for minimal user feedback
        self.console_handler = logging.StreamHandler(sys.stdout)
        self.console_handler.setFormatter(self.formatter)
        self.console_handler.setLevel(logging.INFO)  # Show INFO and above in console
        self.logger.addHandler(self.console_handler)

        # Initialize file handler as None (will be created when saving logs)
        self.file_handler = None

        # Initialize image storage
        self.scoreboard_image: Optional[np.ndarray] = None
        self.summary_image: Optional[np.ndarray] = None
        self.timeline_images: Optional[List[np.ndarray]] = []
        self.error_id = None

    def store_scoreboard(self, image: np.ndarray):
        """Store the scoreboard screenshot."""
        self.scoreboard_image = image.copy()
        self.logger.debug("Stored scoreboard image")

    def store_summary(self, image: np.ndarray):
        """Store the summary screenshot."""
        self.summary_image = image.copy()
        self.logger.debug("Stored summary image")

    def store_timeline(self, image: np.ndarray):
        """Store a timeline screenshot."""
        self.timeline_images.append(image.copy())
        self.logger.debug(f"Stored timeline image #{len(self.timeline_images)}")

    def debug(self, message: str):
        """Log a debug message (file only)."""
        self.logger.debug(message)

    def info(self, message: str):
        """Log an info message (console and file)."""
        self.logger.info(message)

    def warning(self, message: str):
        """Log a warning message (console and file)."""
        self.logger.warning(message)

    def error(self, message: str):
        """Log an error message (console and file)."""
        self.logger.error(message)

    def _generate_error_id(self) -> str:
        """Generate a unique error ID."""
        return 'E' + ''.join(random.choices(string.digits, k=7))

    def _setup_file_logging(self) -> Path:
        """Setup file logging and return the log directory path."""
        # Generate error ID if not exists
        if not self.error_id:
            self.error_id = self._generate_error_id()

        # Create log directory
        documents_path = Path.home() / "Documents"
        base_log_dir = documents_path / "practistics_error_logs"
        error_dir = base_log_dir / self.error_id
        error_dir.mkdir(parents=True, exist_ok=True)

        # Create log file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = error_dir / f"log_{timestamp}.txt"

        # Create and setup file handler
        self.file_handler = logging.FileHandler(log_file)
        self.file_handler.setFormatter(self.formatter)
        self.file_handler.setLevel(logging.DEBUG)  # Capture all logs in file
        self.logger.addHandler(self.file_handler)

        return error_dir

    def save_logs(self, exception_info: Optional[str] = None) -> str:
        """
        Save all logs and images.
        Returns the error ID for reference.
        """
        log_dir = self._setup_file_logging()

        if exception_info:
            self.error(f"Exception Information: {exception_info}")

        # Save scoreboard image if it exists
        if self.scoreboard_image is not None:
            image_path = log_dir / "scoreboard.png"
            cv2.imwrite(str(image_path), self.scoreboard_image)
            self.info("Saved scoreboard image")

        # Save summary image if it exists
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

Logger = Logger()
