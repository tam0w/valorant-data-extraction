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

documents_path = Path.home() / "Documents"
base_log_dir = documents_path / "practistics_error_logs"
FOLDER = base_log_dir / "E4052"


def read_images_from_folder():
    global FOLDER

    image_files = sorted(glob.glob(os.path.join(FOLDER, "*.png")))
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
