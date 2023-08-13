import cv2 as cv
import easyocr
import numpy as np
import pandas as pd
import pyautogui as py
import time
import os

# Load resources

reader = easyocr.Reader(['en'])
agents = pd.read_csv(r'D:\PROJECTS\demo-analysis-timeline\res\agentinfo.csv', header=0)

# Functions
def analyze(rounds):
    """ This function will analyze the returned information from each individual round OCR and POST the
    final dataframe into the API endpoint? Or maybe this function will just give the final dataframe from the TL round
    analysis, into a json converting function which will then be posted into the website, perhaps."""

    df = pd.DataFrame(columns=['first_kill', 'time', 'first_death', 'planted', 'defuse', 'round_win'])

    first_action_times, plants_or_not, fk_player, fk_death = rounds_ss(rounds)

    df['first_kill'] = fk_player
    df['first_death'] = fk_death

    plants = [round_instance.__contains__('Planted') for round_instance in plants_or_not]
    df['planted'] = plants

    defuses = [round_instance.__contains__('Defused') for round_instance in plants_or_not]
    df['defuse'] = defuses

    first_kill_times = []
    first_is_plant = [round_instance[0].__contains__('Planted') for round_instance in plants_or_not]
    print(first_is_plant)
    # first_actions = [round_instance[0] for i, round_instance in enumerate(first_action_times) if first_plants[i]]
    # for i in range(len(plants_or_not)):
    for i, round_instance in enumerate(first_action_times):
        print(round_instance, 'test')
        # first_kill_times = [round_instance[0] if first_is_plant[i] is False else round_instance[1]]
        if first_is_plant[i] is False:
            first_kill_times.append(round_instance[0])
        else:
            first_kill_times.append(round_instance[1])


    df['time'] = first_kill_times


    print(df)


def rounds_ss(total_rounds):
    """ This function will go to the timeline page of the match in question and screenshot every page of the timeline.
    It will then run the OCR function for all the rounds in the match as specified and append them  to a list. This
    list will be returned to the 'analyze' function. """

    time.sleep(2)
    py.leftClick(x=1020, y=190, duration=0.37)
    py.leftClick(x=187, y=333, duration=0.37)
    tl_ss = []
    time.sleep(0.5)

    for i in range(total_rounds):

        py.moveRel(63, 0, duration=0.12)
        py.leftClick()

        if i == 11:
            py.moveRel(-20, 0, duration=0.2)
            continue

        image = py.screenshot()
        cv_image = cv.cvtColor(np.array(image), cv.COLOR_RGB2BGR)
        tl_ss.append(cv_image)

        time.sleep(0.15)

    # The preprocessing and ocr can either be done in this function or another.
    image = py.screenshot()
    cv_image = cv.cvtColor(np.array(image), cv.COLOR_RGB2BGR)
    tl_ss.append(cv_image)

    timestamps, plants = rounds_ocr(tl_ss)
    fk_player, fk_death = match_agent(tl_ss)
    print(plants)

    return timestamps, plants, fk_player, fk_death


def df_to_json():
    """Preferably take in the final dataframe and convert it into the JSON before POSTing into the API endpoint."""


def scoreboard_ocr():
    """Any preprocessing or other shenanigans here. And then perform OCR and return match metadata, individual player
        stats as well as match score / outcome. This can be a data frame. Also, distinctly return total no of rounds."""

    # py.leftClick(x=875, y=190, duration=0.35)
    # scoreboard_ss = py.screenshot()
    # scoreboard_ss = cv.cvtColor(np.array(scoreboard_ss), cv.COLOR_RGB2BGR)
    #
    # return


def rounds_ocr(all_round_images):
    """Perform OCR And preprocessing of all the rounds to extract, which player got the first kill, when they get it
    if the spike was planted or not. Possibly in a dataframe?"""

    all_round_images_cropped = [images[505:970, 980:1040] for images in all_round_images]
    timestamps = [reader.readtext(image, detail=0) for image in all_round_images_cropped]

    all_round_images_cropped_plants = [images[505:970, 1150:1230] for images in all_round_images]
    plants = [reader.readtext(image, detail=0) for image in all_round_images_cropped_plants]

    return timestamps, plants

def match_agent(images):

    """ """
    list_of_agents = agents['names'].to_list()
    indexes_fk = []
    indexes_dt = []
    sprite_path = r'D:\PROJECTS\demo-analysis-timeline\res\sprites'
    dir_list = os.listdir(sprite_path)

    for image in images:
        tl = image[506:539,945:980]
        tl_gray = cv.cvtColor(tl, cv.COLOR_BGR2GRAY)

        tl_dt = image[506:539,1232:1265]
        tl_gray_dt = cv.cvtColor(tl_dt, cv.COLOR_BGR2GRAY)

        values_dt = []
        values = []

        sprite_list = []

        for i, file in enumerate(dir_list):
            file = os.path.join(sprite_path, file)
            img = cv.imread(file, 0)
            sprite_list.append(img)

        for agent in sprite_list:
            agent = cv.resize(agent, (0, 0), fx=0.39, fy=0.39, interpolation=cv.INTER_AREA)

            result = cv.matchTemplate(tl_gray, agent, cv.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
            values.append(max_val)

            result_dt = cv.matchTemplate(tl_gray_dt, agent, cv.TM_CCOEFF_NORMED)
            min_val_dt, max_val_dt, min_loc_dt, max_loc_dt = cv.minMaxLoc(result_dt)
            values_dt.append(max_val_dt)

        indexes_dt.append(values_dt.index(max(values_dt)))
        indexes_fk.append(values.index(max(values)))

    fk_player = [list_of_agents[index] for index in indexes_fk]
    fk_dt = [list_of_agents[index] for index in indexes_dt]

    return fk_player, fk_dt





