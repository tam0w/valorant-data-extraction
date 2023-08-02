import time
import numpy as np
import pyautogui as py
import cv2 as cv


print(py.size())
ss = []

time.sleep(3)

print(py.position())

py.moveTo(1020,190,duration=0.5)
py.leftClick()

py.moveTo(187,333,duration=0.45)
py.leftClick()

imageObj = py.screenshot()
cv_imageObj = cv.cvtColor(np.array(imageObj), cv.COLOR_RGB2BGR)
ss.append(cv_imageObj)
def screenshots_rounds(total_rounds):

    imageObj = py.screenshot()
    cv_imageObj = cv.cvtColor(np.array(imageObj), cv.COLOR_RGB2BGR)
    ss.append(cv_imageObj)

    for i in range(total_rounds):

        py.moveRel(63,0,duration=0.12)
        py.leftClick()

        imageObj = py.screenshot()
        cv_imageObj = cv.cvtColor(np.array(imageObj), cv.COLOR_RGB2BGR)
        ss.append(cv_imageObj)

        if i == 11:
            py.moveRel(-20, 0, duration=0.2)
            continue

screenshots_rounds(23)

print(len(ss))


