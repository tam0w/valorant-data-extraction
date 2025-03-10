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
    return f"session_{timestamp}"


def read_images_from_folder(config: Dict, sub_dir: str) -> Tuple[
    List[np.ndarray], Optional[np.ndarray], Optional[np.ndarray]]:
    """Read images from a specific folder"""
    base_dir = Path(config['log_dir'])
    target_dir = base_dir / sub_dir

    if not target_dir.exists():
        raise FileNotFoundError(f"The directory {target_dir} does not exist.")

    def extract_number(filepath):
        filename = os.path.basename(filepath)
        match = re.search(r'\d+', filename)
        return int(match.group()) if match else float('inf')

    image_files = sorted(glob.glob(os.path.join(target_dir, "*.png")), key=extract_number)

    timeline_images = []
    scoreboard_image = None
    summary_image = None

    for image_file in image_files:
        image = cv.imread(image_file)

        if "scoreboard" in image_file:
            scoreboard_image = cv.cvtColor(image, cv.COLOR_RGB2BGR)
            logger.store_scoreboard(scoreboard_image)
            print("Scoreboard data read.")

        elif "summary" in image_file:
            summary_image = cv.cvtColor(image, cv.COLOR_RGB2BGR)
            logger.store_summary(summary_image)
            print("Summary data read.")

        else:
            timeline = cv.cvtColor(image, cv.COLOR_RGB2BGR)
            logger.store_timeline(timeline)
            timeline_images.append(timeline)
            print("Round", len(timeline_images), "data read.")

    if scoreboard_image is None:
        print('SCOREBOARD DATA NOT READ: Please ensure a scoreboard image is present in the folder.')
    if summary_image is None:
        print('SUMMARY DATA NOT READ: Please ensure a summary image is present in the folder.')

    return timeline_images, scoreboard_image, summary_image


def screenshot_pages() -> Tuple[List[np.ndarray], Optional[np.ndarray], Optional[np.ndarray]]:
    """Capture screenshots of match pages using keyboard input"""
    timeline_images = []
    scoreboard_image = None
    summary_image = None

    print('Waiting to read your game data..')

    # Wait for summary screenshot
    while True:
        if keyboard.is_pressed('s'):
            image = py.screenshot()
            summary_image = cv.cvtColor(np.array(image), cv.COLOR_RGB2BGR)
            print("Meta data obtained.")
            logger.store_summary(summary_image)
            time.sleep(0.15)
            break

    # Wait for scoreboard and timeline screenshots
    while True:
        if keyboard.is_pressed('b'):
            image = py.screenshot()
            scoreboard_image = cv.cvtColor(np.array(image), cv.COLOR_RGB2BGR)
            logger.store_scoreboard(scoreboard_image)
            print("Scoreboard data read.")
            time.sleep(0.3)

        if keyboard.is_pressed('p'):
            image = py.screenshot()
            timeline_screen = cv.cvtColor(np.array(image), cv.COLOR_RGB2BGR)
            logger.store_timeline(timeline_screen)
            timeline_images.append(timeline_screen)
            print("Round", len(timeline_images), "data read. ")
            time.sleep(0.3)

        if keyboard.is_pressed('q'):
            print('Timeline data reading complete.')
            break

    # Make sure scoreboard is captured
    if scoreboard_image is None:
        print('SCOREBOARD DATA NOT READ: Please press b to capture the scoreboard.')

        while True:
            if keyboard.is_pressed('b'):
                image = py.screenshot()
                scoreboard_image = cv.cvtColor(np.array(image), cv.COLOR_RGB2BGR)
                logger.store_scoreboard(scoreboard_image)
                print("Scoreboard data read.")
                time.sleep(0.3)
                break

    print('Processing data..')

    return timeline_images, scoreboard_image, summary_image