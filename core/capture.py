import glob
import os
import re
from pathlib import Path
import cv2 as cv
import keyboard
import time
import pyautogui as py
import numpy as np
from typing import Tuple, List, Dict, Optional
from datetime import datetime
from core.logger import logger


def generate_session_id() -> str:
    """Generate a unique session ID for grouping screenshots"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    session_id = f"session_{timestamp}"
    logger.debug(f"Generated session ID: {session_id}")
    return session_id


def read_images_from_folder(config: Dict, sub_dir: str) -> Tuple[
    List[np.ndarray], Optional[np.ndarray], Optional[np.ndarray]]:
    """
    Read images from a specific folder

    Args:
        config: Application configuration
        sub_dir: The subdirectory to read images from
    """
    logger.push_context(operation="read_images", folder=sub_dir)

    base_dir = Path(config['log_dir'])
    target_dir = base_dir / sub_dir

    timeline_images = []
    scoreboard_image = None
    summary_image = None

    try:
        if not target_dir.exists():
            logger.error(f"The directory {target_dir} does not exist")
            raise FileNotFoundError(f"The directory {target_dir} does not exist.")

        # Function to extract number from filename for sorting
        def extract_number(filepath):
            filename = os.path.basename(filepath)
            match = re.search(r'\d+', filename)
            return int(match.group()) if match else float('inf')

        # Get all PNG files in the directory and sort them
        image_files = sorted(glob.glob(os.path.join(target_dir, "*.png")), key=extract_number)
        logger.debug(f"Found {len(image_files)} PNG files in {target_dir}")

        for image_file in image_files:
            try:
                logger.debug(f"Reading image file: {image_file}")
                image = cv.imread(image_file)

                if image is None:
                    logger.warning(f"Failed to read image: {image_file}")
                    continue

                logger.debug(f"Successfully read image: {image_file}, shape: {image.shape}")

                if "scoreboard" in image_file:
                    scoreboard_image = cv.cvtColor(image, cv.COLOR_RGB2BGR)
                    logger.store_scoreboard(scoreboard_image)
                    logger.info("Scoreboard data read")
                    logger.user_output("Scoreboard data read.")

                elif "summary" in image_file:
                    summary_image = cv.cvtColor(image, cv.COLOR_RGB2BGR)
                    logger.store_summary(summary_image)
                    logger.info("Summary data read")
                    logger.user_output("Summary data read.")

                else:
                    timeline = cv.cvtColor(image, cv.COLOR_RGB2BGR)
                    logger.store_timeline(timeline)
                    timeline_images.append(timeline)
                    round_num = len(timeline_images)
                    logger.info(f"Round {round_num} data read")
                    logger.user_output(f"Round {round_num} data read.")

            except Exception as e:
                logger.error(f"Error processing image file {image_file}: {str(e)}")

        # Warn about missing required images
        if scoreboard_image is None:
            logger.warning('SCOREBOARD DATA NOT READ: No scoreboard image found in the folder')
            logger.user_output('SCOREBOARD DATA NOT READ: Please ensure a scoreboard image is present in the folder.')

        if summary_image is None:
            logger.warning('SUMMARY DATA NOT READ: No summary image found in the folder')
            logger.user_output('SUMMARY DATA NOT READ: Please ensure a summary image is present in the folder.')

        if not timeline_images:
            logger.warning('TIMELINE DATA NOT READ: No timeline images found in the folder')
            logger.user_output('TIMELINE DATA NOT READ: Please ensure timeline images are present in the folder.')
        else:
            logger.info(f"Successfully read {len(timeline_images)} timeline images")

    except Exception as e:
        logger.error(f"Error reading images from folder: {str(e)}")
        raise
    finally:
        logger.clear_context()

    return timeline_images, scoreboard_image, summary_image


def screenshot_pages() -> Tuple[List[np.ndarray], Optional[np.ndarray], Optional[np.ndarray]]:
    """Capture screenshots of match pages using keyboard input"""
    logger.push_context(operation="screenshot_pages")

    timeline_images = []
    scoreboard_image = None
    summary_image = None

    try:
        logger.info('Waiting for user to capture screenshots')
        logger.user_output('Waiting to read your game data..')

        # Wait for summary screenshot
        logger.debug('Waiting for summary screenshot (press S)')
        while True:
            if keyboard.is_pressed('s'):
                logger.debug('S key pressed, capturing summary screenshot')
                image = py.screenshot()
                summary_image = cv.cvtColor(np.array(image), cv.COLOR_RGB2BGR)
                logger.info("Meta data obtained")
                logger.user_output("Meta data obtained.")
                logger.store_summary(summary_image)
                logger.debug(f"Summary screenshot captured, shape: {summary_image.shape}")
                time.sleep(0.15)
                break

        # Wait for scoreboard and timeline screenshots
        logger.debug('Waiting for scoreboard (press B) and timeline (press P) screenshots')
        logger.debug('Press Q to finish capturing')

        while True:
            if keyboard.is_pressed('b'):
                logger.debug('B key pressed, capturing scoreboard screenshot')
                image = py.screenshot()
                scoreboard_image = cv.cvtColor(np.array(image), cv.COLOR_RGB2BGR)
                logger.store_scoreboard(scoreboard_image)
                logger.info("Scoreboard data read")
                logger.user_output("Scoreboard data read.")
                logger.debug(f"Scoreboard screenshot captured, shape: {scoreboard_image.shape}")
                time.sleep(0.3)

            if keyboard.is_pressed('p'):
                logger.debug('P key pressed, capturing timeline screenshot')
                image = py.screenshot()
                timeline_screen = cv.cvtColor(np.array(image), cv.COLOR_RGB2BGR)
                logger.store_timeline(timeline_screen)
                timeline_images.append(timeline_screen)
                round_num = len(timeline_images)
                logger.info(f"Round {round_num} data read")
                logger.user_output(f"Round {round_num} data read. ")
                logger.debug(f"Timeline screenshot {round_num} captured, shape: {timeline_screen.shape}")
                time.sleep(0.3)

            if keyboard.is_pressed('q'):
                logger.info('Timeline data reading complete')
                logger.user_output('Timeline data reading complete.')
                break

        # Make sure scoreboard is captured
        if scoreboard_image is None:
            logger.warning('SCOREBOARD DATA NOT READ: Prompting user to capture scoreboard')
            logger.user_output('SCOREBOARD DATA NOT READ: Please press B to capture the scoreboard.')

            logger.debug('Waiting for scoreboard screenshot (press B)')
            while True:
                if keyboard.is_pressed('b'):
                    logger.debug('B key pressed, capturing scoreboard screenshot')
                    image = py.screenshot()
                    scoreboard_image = cv.cvtColor(np.array(image), cv.COLOR_RGB2BGR)
                    logger.store_scoreboard(scoreboard_image)
                    logger.info("Scoreboard data read")
                    logger.user_output("Scoreboard data read.")
                    logger.debug(f"Scoreboard screenshot captured, shape: {scoreboard_image.shape}")
                    time.sleep(0.3)
                    break

        logger.info('Processing data')
        logger.user_output('Processing data..')

        # Log summary of captured data
        logger.info(f"Captured {len(timeline_images)} timeline images")
        if scoreboard_image is not None:
            logger.info("Captured scoreboard image")
        if summary_image is not None:
            logger.info("Captured summary image")

    except Exception as e:
        logger.error(f"Error during screenshot capture: {str(e)}")
        raise
    finally:
        logger.clear_context()

    return timeline_images, scoreboard_image, summary_image