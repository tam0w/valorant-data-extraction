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
    tl_ss = []
    greens = []
    who_fb = []
    scoreboard = None
    summary = None

    for image_file in image_files:
        image = cv.imread(image_file)
        if "scoreboard" in image_file:
            scoreboard = cv.cvtColor(image, cv.COLOR_RGB2BGR)
            Logger.store_scoreboard(scoreboard)
            print("Scoreboard data read.")

        elif "summary" in image_file:
            summary = cv.cvtColor(image, cv.COLOR_RGB2BGR)
            Logger.store_summary(image)
            print("Summary data read.")

        else:
            cv_image = cv.cvtColor(image, cv.COLOR_RGB2BGR)
            b, g, r = cv_image[520, 1150]
            greens.append(g)
            Logger.store_timeline(image)
            tl_ss.append(cv_image)
            print("Round", len(tl_ss), "data read.")

    if scoreboard is None:
        print('SCOREBOARD DATA NOT READ: Please ensure a scoreboard image is present in the folder.')
    if summary is None:
        print('SUMMARY DATA NOT READ: Please ensure a summary image is present in the folder.')

    return tl_ss, greens, who_fb, scoreboard, summary

# def screenshot_pages():
#
#     while True:
#         if keyboard.is_pressed('s'):
#             rounds, sides, fscore = scores_ocr()
#             print("Meta data obtained.")
#             time.sleep(0.15)
#             break
#
#     tl_ss = []
#     greens = []
#     who_fb = []
#     scoreboard = None
#
#     while True:
#
#         if keyboard.is_pressed('b'):
#             image = py.screenshot()
#             scoreboard = cv.cvtColor(np.array(image), cv.COLOR_RGB2BGR)
#             error_data['scoreboard'] = scoreboard
#             print("Scoreboard data read.")
#             time.sleep(0.3)
#
#         if keyboard.is_pressed('p'):
#             image = py.screenshot()
#             cv_image = cv.cvtColor(np.array(image), cv.COLOR_RGB2BGR)
#             b, g, r = cv_image[520, 1150]
#             greens.append(g)
#             tl_ss.append(cv_image)
#             print("Round", len(tl_ss), "data read. ")
#             time.sleep(0.3)
#
#         if keyboard.is_pressed('q'):
#             print('Timeline data reading complete.')
#             error_data['timeline'] = tl_ss
#             break
#
#     if scoreboard is None:
#         print('SCOREBOARD DATA NOT READ: Please press b to capture the scoreboard.')
#
#         while True:
#             if keyboard.is_pressed('b'):
#                 image = py.screenshot()
#                 scoreboard = cv.cvtColor(np.array(image), cv.COLOR_RGB2BGR)
#                 error_data['scoreboard'] = scoreboard
#                 print("Scoreboard read. Processing data..")
#                 time.sleep(0.3)
#                 break
#     else:
#         print('Processing data..')