import time
import numpy as np
import pyautogui as py
import cv2 as cv

time.sleep(3)


def go_timeline():
    py.leftClick(x=1020, y=190, duration=0.35)
    py.leftClick(x=187, y=333, duration=0.3)


def screenshots_rounds(total_rounds):
    tl_ss = []

    image = py.screenshot()
    cv_image = cv.cvtColor(np.array(image), cv.COLOR_RGB2BGR)
    tl_ss.append(cv_image)

    for i in range(total_rounds):

        py.moveRel(63, 0, duration=0.12)
        py.leftClick()

        if i == 11:
            py.moveRel(-20, 0, duration=0.2)
            continue

        image = py.screenshot()
        cv_image = cv.cvtColor(np.array(image), cv.COLOR_RGB2BGR)
        tl_ss.append(cv_image)

    return tl_ss


go_timeline()

scrim1 = screenshots_rounds(19)

print(len(scrim1))
