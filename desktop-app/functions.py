import time, numpy as np, pyautogui as py, cv2 as cv, pandas as pd, easyocr

reader = easyocr.Reader(['en'])
def go_timeline():
    py.leftClick(x=1020, y=190, duration=0.35)
    py.leftClick(x=187, y=333, duration=0.3)


def rounds_ss(total_rounds):
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

    # The preprocessing and ocr can either be done in this function or another.

    return tl_ss

def scoreboard_ocr():
    py.leftClick(x=875, y=190, duration=0.35)
    scoreboard_ss = py.screenshot()
    scoreboard_ss = cv.cvtColor(np.array(scoreboard_ss), cv.COLOR_RGB2BGR)
    """Any preprocessing or other shenanigans here. And then perform OCR and return match metadata, individual player
    stats aswell as match score / outcome. This can be a data frame. Also distinctly return total no of rounds."""
    # return

def rounds_ocr(all_round_images):
    '''Perform OCR And preprocessing of all the rounds to extract, which player got the first kill, when they get it
    if the spike was planted or not. Possibly in a dataframe?'''

    rounds = pd.DataFrame(['first_kill','time','opponent','planted','round_win'])
    all_round_images_cropped = [for images[505:840,980:1040] in all_round_images]
    timestamps = [reader.readtext(image,detail=0) for image in all_round_images_cropped]

    # Perform your preprocessing and OCR here. If all preprocessing is the same, we can make that a seperate function.
    return timestamps