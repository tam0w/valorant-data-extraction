import logging
import sys
import random
import string
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any, Union
import cv2
import numpy as np
import colorama

# Initialize colorama for colored terminal output
colorama.init()


class ColoredFormatter(logging.Formatter):
    """
    Custom formatter that adds colors to the log output
    """
    COLORS = {
        'DEBUG': colorama.Fore.CYAN,
        'INFO': colorama.Fore.GREEN,
        'WARNING': colorama.Fore.YELLOW,
        'ERROR': colorama.Fore.RED,
        'CRITICAL': colorama.Fore.RED + colorama.Style.BRIGHT
    }

    def format(self, record):
        log_message = super().format(record)
        return self.COLORS.get(record.levelname, colorama.Fore.WHITE) + log_message + colorama.Style.RESET_ALL


class Logger:
    """
    Enhanced logger module that separates user-facing output from debug logs
    and provides contextual debugging information
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
        self.logger.propagate = False  # Prevent propagation to root logger

        # Create formatters
        self.debug_formatter = ColoredFormatter(
            '%(asctime)s - [%(levelname)s] - %(name)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        self.console_formatter = ColoredFormatter(
            '[%(levelname)s] %(message)s'
        )

        # Console handler for normal logs
        self.console_handler = logging.StreamHandler(sys.stdout)
        self.console_handler.setFormatter(self.console_formatter)
        self.console_handler.setLevel(logging.INFO)  # Default level
        self.logger.addHandler(self.console_handler)

        # File handler will be created on demand
        self.file_handler = None

        # Current context information
        self.context = {}

        # Verbose mode flag
        self.dev_mode = False

        # User output stream for clean user-facing messages
        # This separates user output from developer logs
        self.user_output_enabled = True

        # Image storage
        self.scoreboard_image = None
        self.summary_image = None
        self.timeline_images = []
        self.error_id = None

    def set_log_level(self, level: Union[str, int]):
        """Set the log level for console output"""
        if isinstance(level, str):
            level = getattr(logging, level.upper())
        self.console_handler.setLevel(level)
        self.logger.debug(f"Log level set to {logging.getLevelName(level)}")

    def set_dev_mode(self, enabled: bool):
        """Enable or disable development mode with verbose logging"""
        self.dev_mode = enabled
        if enabled:
            self.set_log_level(logging.DEBUG)
            self.user_output("Development mode enabled - verbose logging active")
        else:
            self.set_log_level(logging.INFO)

    def enable_user_output(self, enabled: bool):
        """Enable or disable user-facing output"""
        self.user_output_enabled = enabled

    def push_context(self, **kwargs):
        """Add contextual information to logs"""
        self.context.update(kwargs)

    def clear_context(self):
        """Clear all contextual information"""
        self.context.clear()

    def get_context_string(self):
        """Get a formatted string of the current context"""
        if not self.context:
            return ""

        parts = []
        for key, value in self.context.items():
            parts.append(f"{key}={value}")

        return f"[{' | '.join(parts)}] "

    def store_scoreboard(self, image: np.ndarray):
        """Store the scoreboard image for debugging"""
        self.scoreboard_image = image.copy()
        self.debug("Stored scoreboard image")

    def store_summary(self, image: np.ndarray):
        """Store the summary image for debugging"""
        self.summary_image = image.copy()
        self.debug("Stored summary image")

    def store_timeline(self, image: np.ndarray):
        """Store a timeline image for debugging"""
        self.timeline_images.append(image.copy())
        self.debug(f"Stored timeline image #{len(self.timeline_images)}")

    def user_output(self, message: str):
        """Output a message intended for the end user"""
        if self.user_output_enabled:
            print(f"{colorama.Fore.WHITE}{message}{colorama.Style.RESET_ALL}")

    def debug(self, message: str):
        """Log a debug message with context"""
        context = self.get_context_string()
        self.logger.debug(f"{context}{message}")

    def info(self, message: str):
        """Log an info message with context"""
        context = self.get_context_string()
        self.logger.info(f"{context}{message}")

    def warning(self, message: str):
        """Log a warning message with context"""
        context = self.get_context_string()
        self.logger.warning(f"{context}{message}")

    def error(self, message: str):
        """Log an error message with context"""
        context = self.get_context_string()
        self.logger.error(f"{context}{message}")

    def critical(self, message: str):
        """Log a critical error message with context"""
        context = self.get_context_string()
        self.logger.critical(f"{context}{message}")

    def _generate_error_id(self) -> str:
        """Generate a unique error ID"""
        return 'E' + ''.join(random.choices(string.digits, k=7))

    def _setup_file_logging(self, config: Dict[str, Any]) -> Path:
        """Set up file logging with the full debug information"""
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
        self.file_handler.setFormatter(self.debug_formatter)
        self.file_handler.setLevel(logging.DEBUG)  # Always log everything to file
        self.logger.addHandler(self.file_handler)

        self.debug(f"Log directory: {log_dir}")

        return log_dir

    def save_logs(self, config: Dict[str, Any], exception_info: Optional[str] = None) -> str:
        """Save logs and screenshots to disk in case of an error"""
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