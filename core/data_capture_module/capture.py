import glob
import os
from pathlib import Path
import cv2 as cv
import keyboard
import time
import pyautogui as py
import matplotlib.pyplot as plt
import numpy as np

# Internal Packages
from core.logger_module.logger import Logger

# Define base directory in Documents folder
documents_path = Path.home() / "Documents"
base_dir = documents_path / "practistics" / "error_logs"


def read_images_from_folder(sub_dir):
    """
    Read images from the specified subdirectory within the error logs folder and return the timeline, scoreboard, and summary images.

    Args:
        sub_dir (str): The name of the subdirectory within error logs to read images from.

    Returns:
        tuple: A tuple containing:

            - timeline_images (list): List of timeline images.

            - scoreboard_image (numpy.ndarray or None): The scoreboard image.

            - summary_image (numpy.ndarray or None): The summary image.
    """
    target_dir = base_dir / sub_dir
    if not target_dir.exists():
        raise FileNotFoundError(f"The directory {target_dir} does not exist.")

    image_files = sorted(glob.glob(os.path.join(target_dir, "*.png")))
    timeline_images = []
    scoreboard_image = None
    summary_image = None

    for image_file in image_files:
        image = cv.imread(image_file)

        if "scoreboard" in image_file:
            scoreboard_image = cv.cvtColor(image, cv.COLOR_RGB2BGR)
            Logger.store_scoreboard(scoreboard_image)
            print("Scoreboard data read.")

        elif "summary" in image_file:
            summary_image = cv.cvtColor(image, cv.COLOR_RGB2BGR)
            Logger.store_summary(image)
            print("Summary data read.")

        else:
            timeline = cv.cvtColor(image, cv.COLOR_RGB2BGR)
            Logger.store_timeline(timeline)
            timeline_images.append(timeline)
            print("Round", len(timeline_images), "data read.")

    if scoreboard_image is None:
        print('SCOREBOARD DATA NOT READ: Please ensure a scoreboard image is present in the folder.')
    if summary_image is None:
        print('SUMMARY DATA NOT READ: Please ensure a summary image is present in the folder.')

    return timeline_images, scoreboard_image, summary_image

def screenshot_pages():
    """
    Capture screenshots of the summary, scoreboard, and timeline pages.

    Returns:
        tuple: A tuple containing:

            - timeline_images (list): List of timeline images.

            - scoreboard_image (numpy.ndarray or None): The scoreboard image.

            - summary_image (numpy.ndarray or None): The summary image.
    """
    timeline_images = []
    scoreboard_image = None

    while True:
        if keyboard.is_pressed('s'):
            image = py.screenshot()
            summary_image = cv.cvtColor(np.array(image), cv.COLOR_RGB2BGR)
            print("Meta data obtained.")
            Logger.store_summary(summary_image)
            time.sleep(0.15)
            break

    while True:
        if keyboard.is_pressed('b'):
            image = py.screenshot()
            scoreboard_image = cv.cvtColor(np.array(image), cv.COLOR_RGB2BGR)
            Logger.store_scoreboard(scoreboard_image)
            print("Scoreboard data read.")
            time.sleep(0.3)

        if keyboard.is_pressed('p'):
            image = py.screenshot()
            timeline_screen = cv.cvtColor(np.array(image), cv.COLOR_RGB2BGR)
            Logger.store_timeline(timeline_screen)
            timeline_images.append(timeline_screen)
            print("Round", len(timeline_images), "data read. ")
            time.sleep(0.3)

        if keyboard.is_pressed('q'):
            print('Timeline data reading complete.')
            break

    if scoreboard_image is None:
        print('SCOREBOARD DATA NOT READ: Please press b to capture the scoreboard.')

        while True:
            if keyboard.is_pressed('b'):
                image = py.screenshot()
                scoreboard_image = cv.cvtColor(np.array(image), cv.COLOR_RGB2BGR)
                Logger.store_scoreboard(scoreboard_image)
                print("Scoreboard data read.")
                time.sleep(0.3)
    else:
        print('Processing data..')

    return timeline_images, scoreboard_image, summary_image