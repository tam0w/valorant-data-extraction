from datetime import datetime
import cv2 as cv
import easyocr
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pyautogui as py
import time
import os

# Load resources

reader = easyocr.Reader(['en'])
agents = pd.read_csv(r'D:\PROJECTS\demo-analysis-timeline\res\agentinfo.csv', header=0)
header = ['first_kill', 'time', 'first_death', 'planted', 'fb_team',
          'defuse', 'side', 'fb_players', 'dt_players', 'team_buy', 'oppo_buy', 'round_win']


# Functions


def analyze():
    """ This function will analyze the returned information from each individual round OCR and POST the
    final dataframe into the API endpoint? Or maybe this function will just give the final dataframe from the TL round
    analysis, into a json converting function which will then be posted into the website, perhaps."""

    df = pd.DataFrame(columns=header)

    rounds, sides = scores_ocr()
    map_name = get_metadata()
    (first_action_times, plants_or_not, fk_player, fk_death, outcomes,
     fb_team, players_agents, buy_info_team, buy_info_oppo) = rounds_ss(rounds)

    df['side'] = sides[:rounds]
    df['round_win'] = outcomes
    df['first_kill'] = fk_player
    df['first_death'] = fk_death
    df['fb_team'] = fb_team
    df['team_buy'] = buy_info_team
    df['oppo_buy'] = buy_info_oppo

    plants = [round_instance.__contains__('Planted') for round_instance in plants_or_not]
    df['planted'] = plants

    defuses = [round_instance.__contains__('Defused') for round_instance in plants_or_not]
    df['defuse'] = defuses

    first_kill_times = []
    first_is_plant = [round_instance[0].__contains__('Planted') for round_instance in plants_or_not]

    for i, round_instance in enumerate(first_action_times):

        if first_is_plant[i] is False:
            first_kill_times.append(round_instance[0])

        else:
            first_kill_times.append(round_instance[1])

    df['time'] = first_kill_times
    df.index += 1

    fbs_players, dt_players = map_player_agents(fb_team, fk_player, fk_death, players_agents)
    df['fb_players'] = fbs_players
    df['dt_players'] = dt_players

    date = datetime.now()
    dt_string = date.strftime("%d_%m_%Y_time_%H_%M")

    df.to_csv(path_or_buf=rf'D:\PROJECTS\demo-analysis-timeline\res\scrims\{map_name}_{dt_string}.csv',
              sep='\t', header=header)
    print(df)


def rounds_ss(total_rounds):
    """ This function will go to the timeline page of the match in question and screenshot every page of the timeline.
    It will then run the OCR function for all the rounds in the match as specified and append them  to a list. This
    list will be returned to the 'analyze' function. """

    tl_ss = []
    greens = []
    who_fb = []

    while True:
        if py.keyboard.is_pressed('p'):
            image = py.screenshot()
            cv_image = cv.cvtColor(np.array(image), cv.COLOR_RGB2BGR)
            b, g, r = cv_image[520, 1150]
            greens.append(g)
            tl_ss.append(cv_image)
            plt.imshow(cv_image)
            plt.show()
            time.sleep(0.5)

        if py.keyboard.is_pressed('q'):
            break

    players_agents, agents_names = zip_player_agents()
    agent_list = all_agents()
    timestamps, plants, buy_info_team, buy_info_oppo = rounds_ocr(tl_ss)
    fk_player, fk_death = match_agent(agent_list, tl_ss, agents_names)
    outcomes = ocr_round_win(tl_ss)

    for green in greens:
        flag = 'you' if green > 100 else 'opponent'
        who_fb.append(flag)

    return timestamps, plants, fk_player, fk_death, outcomes, who_fb, players_agents, buy_info_team, buy_info_oppo


def df_to_json():
    """Preferably take in the final dataframe and convert it into the JSON before POSTing into the API endpoint."""


def scores_ocr():
    """Any preprocessing or other shenanigans here. And then perform OCR and return match metadata, individual player
        stats as well as match score / outcome. This can be a data frame. Also, distinctly return total no of rounds."""
    time.sleep(2)
    sides = side_first_half()
    time.sleep(0.15)

    my_rounds, match_result, opp_rounds = final_score_ocr()
    print("Score:", my_rounds, "-", opp_rounds, "\nResult: ", match_result)
    total_rounds = int(my_rounds) + int(opp_rounds)

    return total_rounds, sides


def rounds_ocr(all_round_images):
    """Perform OCR And preprocessing of all the rounds to extract, which player got the first kill, when they get it
    if the spike was planted or not. Possibly in a dataframe?"""

    buys = [images[425:480, 1020:1145] for images in all_round_images]
    buy_info = [reader.readtext(image, allowlist=['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', ','], detail=0) for
                image in buys]
    buy_info_team = [buy[0] for buy in buy_info]
    buy_info_oppo = [buy[1] for buy in buy_info]

    all_round_images_cropped = [images[505:970, 980:1040] for images in all_round_images]
    timestamps = [reader.readtext(image, detail=0) for image in all_round_images_cropped]

    all_round_images_cropped_plants = [images[505:970, 1150:1230] for images in all_round_images]
    plants = [reader.readtext(image, detail=0) for image in all_round_images_cropped_plants]

    return timestamps, plants, buy_info_team, buy_info_oppo


def all_agents():
    ss = py.screenshot()
    image = cv.cvtColor(np.array(ss), cv.COLOR_RGB2BGR)
    agent_list = []

    st_u = 503
    gr_check = 161

    for i in range(5):

        b, g, r = image[st_u, gr_check]
        u = st_u

        while g < 180:
            u = u + 1
            b, g, r = image[u, gr_check]

        st_l = gr_check + 3
        b, new_g, r = image[u, st_l]
        cur_img = image[u:u + 40, st_l:st_l + 40]
        st_u = u + 42

        agent_list.append(cur_img)

    st_u = 726

    for i in range(5):

        b, g, r = image[st_u, gr_check]
        u = st_u
        while r < 180:
            u = u + 1
            b, g, r = image[u, gr_check]

        st_l = gr_check + 3
        b, g, new_r = image[u, st_l]
        cur_img = image[u:u + 40, st_l:st_l + 40]
        st_u = u + 42

        agent_list.append(cur_img)

    return agent_list


def match_agent(agent_images, images, agents_names):
    """This function matches all the agents first kills and death sprites to their actual agent names and returns
    what agent got the first kill and died first."""

    indexes_fk = []
    indexes_dt = []

    for image in images:
        tl = image[506:542, 945:980]
        tl_dt = image[506:539, 1232:1265]

        values_dt = []
        values = []

        for agent in agent_images:
            result = cv.matchTemplate(tl, agent, cv.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
            values.append(max_val)

            result_dt = cv.matchTemplate(tl_dt, agent, cv.TM_CCOEFF_NORMED)
            min_val_dt, max_val_dt, min_loc_dt, max_loc_dt = cv.minMaxLoc(result_dt)
            values_dt.append(max_val_dt)

        indexes_dt.append(values_dt.index(max(values_dt)))
        indexes_fk.append(values.index(max(values)))

    fk_player = [agents_names[index] for index in indexes_fk]
    fk_dt = [agents_names[index] for index in indexes_dt]

    return fk_player, fk_dt


def ocr_round_win(images):
    round_outcomes = []

    for image in images:
        file = image[430:470, 130:700]
        gray = cv.cvtColor(file, cv.COLOR_BGR2GRAY)
        round_outcome = reader.readtext(gray, detail=0)
        if round_outcome.__str__().upper().__contains__('LOSS'):
            round_outcomes.append('loss')
        else:
            round_outcomes.append('win')
    return round_outcomes


def final_score_ocr():
    image = py.screenshot()
    cv_image = cv.cvtColor(np.array(image), cv.COLOR_RGB2BGR)
    score = cv_image[70:170, 700:1150]
    score = reader.readtext(score, detail=0)

    return score[0].__str__(), score[1].__str__(), score[2].__str__()


def get_metadata():
    image = py.screenshot()
    cv_image = cv.cvtColor(np.array(image), cv.COLOR_RGB2BGR)
    file = cv_image[125:145, 120:210]
    gray = cv.cvtColor(file, cv.COLOR_BGR2GRAY)
    gray = cv.convertScaleAbs(gray, 1, 5)
    result = reader.readtext(gray, detail=0)
    return result[0].__str__().lower()


def zip_player_agents():
    image = py.screenshot()
    cv_image = cv.cvtColor(np.array(image), cv.COLOR_RGB2BGR)
    file = cv_image[495:940, 150:370]
    gray = cv.cvtColor(file, cv.COLOR_RGB2BGR)
    result = reader.readtext(gray, detail=0)
    player_names = [name for name in result if (result.index(name) % 2) == 0]
    agent_names = [name for name in result if (result.index(name) % 2) == 1]
    player_agents_zipped = dict(zip(player_names, agent_names))
    return player_agents_zipped, agent_names


def side_first_half():
    image = py.screenshot()
    cv_image = cv.cvtColor(np.array(image), cv.COLOR_RGB2BGR)
    file = cv_image[300:400, 1300:1500]
    gray = cv.cvtColor(file, cv.COLOR_RGB2BGR)
    res1 = reader.readtext(gray, detail=0)
    result = res1[0].__str__().lower()

    if result.__contains__('def'):
        first = "Defense"
        second = "Attack"
    else:
        second = "Defense"
        first = "Attack"
    sides = ([first] * 12 + [second] * 12)

    return sides


def map_player_agents(who_fb, fk_player, fk_dt, players_agents):
    players_agents_team = dict(list(players_agents.items())[:5])
    players_agents_oppo = dict(list(players_agents.items())[5:])
    players_agents_team = {value: key for key, value in players_agents_team.items()}
    players_agents_oppo = {value: key for key, value in players_agents_oppo.items()}
    print("Your team:", players_agents_team, "\n", "Oppoennt:", players_agents_oppo)

    final_player_fk_list = []
    final_opponent_dt_list = []

    for i, agent in enumerate(fk_player):

        if who_fb[i] == 'you':
            final_player_fk_list.append(players_agents_team.get(agent))
        else:
            final_player_fk_list.append(players_agents_oppo.get(agent))

    for i, agent in enumerate(fk_dt):

        if who_fb[i] == 'opponent':
            final_opponent_dt_list.append(players_agents_team.get(agent))
        else:
            final_opponent_dt_list.append(players_agents_oppo.get(agent))

    return final_player_fk_list, final_opponent_dt_list
