import random
import sys
import traceback
from datetime import datetime
from difflib import get_close_matches
import cv2 as cv
import easyocr
import numpy as np
import pyautogui as py
import time
import os
import keyboard
import requests
import matplotlib.pyplot as plt

# Internal packages
from core.logger_module import logger
from core.data_capture_module import capture

logger = logger.Logger()


def auth():
    key = input('Insert your authentication key:')
    header = {'Authorization': f'Bearer {key}'}
    test = requests.post('https://practistics.live/app/api/verify', headers=header)

    if test.status_code == 200:
        return key

    else:
        print('Token expired / invalid.')
        return 0


def run_app_main():
    global reader
    reader = easyocr.Reader(['en'])

    # jwt = 0
    jwt = "dev"  # for dev environments

    while True:

        # if jwt == 0:
        #     jwt = auth()
        #     continue

        ans = input('Please type \'start\' when you would like to begin or \'exit\' if you are finished.\n')
        if ans == 'start':

            try:
                analyze(jwt)

            except Exception:
                print(f"Error! Try again or report on discord (please note the error id!).")
                confirmation = True if input('Would you like to send an error log? (y/n):').lower() == 'y' else False
                error_data['traceback'] = traceback.format_exc()
                if confirmation:
                    store_error_data()
                continue

        if ans == 'exit':
            exit()


def init_function():
    print(1.6)


if len(sys.argv) == 1:
    print("Please use the launcher.")
    if input("") == "dev": run_app_main()

if len(sys.argv) > 1 and sys.argv[1] == "init":
    init_function()

if len(sys.argv) > 1 and sys.argv[1] == "main":
    run_app_main()


def analyze(creds):
    """ This function will analyze the returned information from each individual round OCR and POST the
    final dataframe into the API endpoint? Or maybe this function will just give the final dataframe from the TL round
    analysis, into a json converting function which will then be posted into the website, perhaps."""

    error_data['local_vars'] = locals()
    (action_times, plants, defuses, fk_player, fk_death, true_fb, outcomes, fb_team, players_agents,
     awp_info, fscore, buy_info_team, buy_info_oppo, map_name, kills_team, kills_opp, first_is_plant, sides, rounds,
     bombsites, all_round_data, anchor_times, kills, assists, scoreboard_values) = rounds_ss()
    error_data['local_vars'] = locals()
    # first_kill_times, second_kill_times = first_and_second_kills(action_times, first_is_plant)
    fbs_players, dt_players = map_player_agents(fb_team, fk_player, fk_death, players_agents)
    error_data['local_vars'] = locals()
    date = datetime.now()
    dt_string = date.strftime("%d/%m/%Y")

    data = {}

    lists = [action_times, plants, defuses, fk_player, fk_death, outcomes, fb_team, awp_info, buy_info_team,
             buy_info_oppo, kills_team, kills_opp, first_is_plant, sides, fbs_players, dt_players, first_kill_times,
             rounds, bombsites, true_fb, fscore, map_name, dt_string, players_agents, anchor_times, all_round_data,
             kills, assists, scoreboard_values]
    error_data['local_vars'] = locals()
    names = ["first_action_times", "plants", "defuses", "fk_player", "fk_death", "outcomes", "fb_team", "awp_info",
             "buy_info_team", "buy_info_oppo", "kills_team", "kills_opp", "first_is_plant", "sides", "fbs_players",
             "dt_players", "first_kill_times", "rounds", "bombsites", "true_fb", "fscore", "map_name", "dt_string",
             "players_agents", "anchor_times", "all_round_data", "kills", "assists", "scoreboard"]

    for name, lst in zip(names, lists):
        data[name] = lst

    if creds == "dev":
        store_error_data()
        return True

    header = {'Authorization': f'Bearer {creds}'}

    test = requests.post('https://practistics.live/app/api', json=data, headers=header)
    # test = requests.post('http://127.0.0.1:5000/app/api', json=data, headers=header)

    if test.status_code == 200:
        print("Data extraction complete, and loaded onto web-server.")
    else:
        print("Error in sending the data. \n")
        confirmation = True if input('Would you like to send an error log? (y/n):').lower() == 'y' else False
        error_data['traceback'] = traceback.format_exc()
        if confirmation:
            store_error_data()

# TODO: Move this to capture module and also make a copy of this function to read from folder rather than screenshot for testing purposes.
def rounds_ss():
    """ This function will go to the all the post-match pages of the match in question and screenshot every page of the timeline.
    It will then run the OCR function for all the rounds in the match as specified and append them  to a list. This
    list will be returned to the 'analyze' function. """

    tl_ss, greens, who_fb, scoreboard, summary = capture.read_images_from_folder()
    # TODO: Move all this fucking logic to helper functions and into their own modules
    scoreboard_val = scoreboard_ocr(scoreboard)
    players_agents, agents_names = zip_player_agents(tl_ss[0])
    agent_list = all_agents(tl_ss[0])
    timestamps, plants_or_not, buy_info_team, buy_info_oppo, awps = rounds_ocr(tl_ss)
    outcomes = ocr_round_win(tl_ss)
    map_info = get_metadata(tl_ss)
    events_team, events_opp, event_sides = total_events(tl_ss)
    site_list = bombsites_plants(tl_ss, map_info)
    awp_information = awp_info(awps)
    kills, assists = kill_ass_kast(tl_ss)

    plants = [round_instance.__contains__('Planted') for round_instance in plants_or_not]
    defuses = [round_instance.__contains__('Defused') for round_instance in plants_or_not]
    first_is_plant = [round_instance[0].__contains__('Planted') for round_instance in plants_or_not]
    sec_is_plant = [round_instance[1].__contains__('Planted') for round_instance in plants_or_not]

    for green in greens:
        flag = 'team' if green > 100 else 'opponent'
        who_fb.append(flag)

    for i in range(len(events_team)):
        if plants[i] is True:

            if sides[i] == 'Attack':
                events_team[i] -= 1
            else:
                events_opp[i] -= 1

        if defuses[i] is True:
            if sides[i] == 'Defense':
                events_team[i] -= 1
            else:
                events_opp[i] -= 1

    (first_eng_left, sec_eng_left, third_eng_left, fourth_eng_left, first_eng_right, sec_eng_right, third_eng_right,
     fourth_eng_right, round_agents) = match_agent(agent_list, tl_ss, agents_names, timestamps)

    all_round_data = generate_all_round_info(round_agents, event_sides, plants_or_not, timestamps)

    anchor_times = []

    for r, round_instance in enumerate(all_round_data):

        for event in round_instance:

            if event == round_instance[-1]:
                if event[-1] == "Kill":
                    anchor_times.append(0)
                    break

            if event[-1] == "Spike":
                anchor_times.append(event[2])
                break

            if event[-1] == "Kill":
                continue

    fk_player = []
    fk_death = []

    sk_player = []
    sk_death = []

    tk_player = []
    tk_death = []

    for i, first_plant in enumerate(first_is_plant):

        if not first_plant:
            fk_player.append(first_eng_left[i])
            fk_death.append(first_eng_right[i])

            if not sec_is_plant[i]:
                sk_player.append(sec_eng_left[i])
                sk_death.append(sec_eng_right[i])

                tk_player.append(third_eng_left[i])
                tk_death.append(third_eng_right[i])

            else:
                sk_player.append(third_eng_left[i])
                sk_death.append(third_eng_right[i])

                tk_player.append(fourth_eng_left[i])
                tk_death.append(fourth_eng_right[i])

        if first_plant:
            fk_player.append(sec_eng_left[i])
            fk_death.append(sec_eng_right[i])

            sk_player.append(third_eng_left[i])
            sk_death.append(third_eng_right[i])

            tk_player.append(fourth_eng_left[i])
            tk_death.append(fourth_eng_right[i])

    true_fb = []

    for i in range(len(timestamps)):

        if fk_player[i] == sk_death[i]:

            if event_sides[i][0] != event_sides[i][1]:
                true_fb.append(False)
            else:
                true_fb.append(True)

        elif fk_player[i] == tk_death[i]:

            first = timestamps[i][0]
            second = timestamps[i][2]

            if int(second) - int(first) <= 10:
                true_fb.append(False)
            else:
                true_fb.append(True)

        else:
            true_fb.append(True)

    return (timestamps, plants, defuses, fk_player, fk_death, true_fb, outcomes, who_fb, players_agents, awp_information
            , fscore, buy_info_team, buy_info_oppo, map_info, events_team, events_opp, first_is_plant, sides, rounds,
            site_list, all_round_data, anchor_times, kills, assists, scoreboard_val)


def generate_all_round_info(round_agents, event_sides, plants_or_not, timestamps):
    all_round_data = round_agents

    for r, round_instance in enumerate(all_round_data):
        for i, timestamp in enumerate(timestamps[r]):

            round_instance[i].append(timestamp)
            round_instance[i].append(event_sides[r][i])
            try:
                if plants_or_not[r][i] == "Planted" or plants_or_not[r][i] == "Defused":
                    round_instance[i].append('Spike')

                else:
                    round_instance[i].append('Kill')
            except IndexError:
                round_instance[i].append('Kill')

    return all_round_data


def first_and_second_kills(action_times, first_is_plant):
    first_kill_times = []
    second_kill_times = []

    for i, round_instance in enumerate(action_times):

        if first_is_plant[i] is False:
            first_kill_times.append(round_instance[0])
            second_kill_times.append(round_instance[1])

        else:
            first_kill_times.append(round_instance[1])
            second_kill_times.append(round_instance[2])

    return first_kill_times, second_kill_times


def awp_info(awps):
    awp_info = []

    for i, awp in enumerate(awps):

        indexes = [idx for idx, value in enumerate(awp) if value == 'Operator']

        if len(indexes) == 0:
            awp_info.append('none')

        elif len(indexes) == 1:
            if indexes[0] < 11:
                awp_info.append('team')
            else:
                awp_info.append('opponent')

        elif len(indexes) == 2:

            if indexes[0] < 11 & indexes[1] < 11:
                awp_info.append('team')
            elif indexes[0] > 10 & indexes[1] > 10:
                awp_info.append('opponent')
            else:
                awp_info.append('both')

        elif len(indexes) > 2:
            awp_info.append('both')

        else:
            awp_info.append('none')

    return awp_info


def df_to_json():
    """Preferably take in the final dataframe and convert it into the JSON before POSTing into the API endpoint."""


def scores_ocr(summary_image):
    """This function will extract the final score of the match and the result of the match from the summary image."""

    sides = side_first_half(summary_image)
    my_rounds, match_result, opp_rounds = final_score_ocr(summary_image)

    if my_rounds.isalpha():
        my_rounds = input("Please confirm the your teams rounds won:")

    if opp_rounds.isalpha():
        opp_rounds = input("Please confirm the opponents rounds won:")

    fscore = my_rounds + " - " + opp_rounds
    print("Score:", fscore, "\nResult: ", match_result)
    total_rounds = int(my_rounds) + int(opp_rounds)

    return total_rounds, sides, fscore


def scoreboard_ocr(img):
    """Gets the OCR value of the scoreboard and returns the values of the scoreboard in a list of lists. Each list contains
    the player IGN, kills, deaths, assists and which side they are on. This function will also ask for user input if the
    OCR fails to read the values."""
    start = 340

    scoreboard = []

    for i in range(10):

        img1 = img[start:start + 50, 330:700]
        res_name = reader.readtext(img1, detail=0, link_threshold=0)

        img1 = img[start:start + 50, 823:873]
        res_kills = reader.readtext(img1, allowlist=['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'], mag_ratio=2.5,
                                    link_threshold=0, text_threshold=0, threshold=0, detail=0)

        img1 = img[start:start + 50, 880:930]
        res_deaths = reader.readtext(img1, allowlist=['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'], mag_ratio=2.5,
                                     link_threshold=0, text_threshold=0, threshold=0, detail=0)

        img1 = img[start:start + 50, 930:980]
        res_assists = reader.readtext(img1, allowlist=['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'], mag_ratio=2.5,
                                      link_threshold=0, text_threshold=0, threshold=0, detail=0)

        if not res_assists:
            res_assists = [input(f'Please confirm the assists for player {res_name}:')]
        elif not res_kills:
            res_kills = [input(f'Please confirm the kills for player {res_name}:')]
        elif not res_deaths:
            res_deaths = [input(f'Please confirm the deaths for player {res_name}:')]
        elif not res_name:
            res_deaths = [input(f'Please confirm the IGN for player number {i + 1} (according to scoreboard):')]

        b1, g1, r1 = img[start + 25, 278]

        if g1 < 100 and r1 > 200 and b1 < 100:
            side = 'opponent'

        else:
            side = 'team'

        scoreboard.append([res_name[0], res_kills[0], res_deaths[0], res_assists[0], side])

        start = start + 52

    return scoreboard


def kill_ass_kast(images):
    kills = []
    assists = []

    for img in images:

        start = 504
        rounds_kills = []
        rounds_assists = []
        start_oppo = 725

        for i in range(10):

            if i < 5:

                img1 = img[start:start + 38, 450:590]

                try:
                    res = reader.readtext(img1, mag_ratio=2.2, detail=0, text_threshold=0, threshold=0,
                                          link_threshold=0,
                                          allowlist='0123456')
                    start = start + 42

                    score = res[0]
                    rounds_kills.append(score[0])
                    rounds_assists.append(score[1])
                except:
                    res = reader.readtext(img1, detail=0, text_threshold=0, threshold=0,
                                          link_threshold=0,
                                          allowlist='0123456')
                    start = start + 42

                    score = res[0]
                    rounds_kills.append(score[0])
                    rounds_assists.append(score[1])

            else:

                img2 = img[start_oppo:start_oppo + 38, 450:590]

                try:
                    res = reader.readtext(img2, mag_ratio=2.2, detail=0, text_threshold=0, threshold=0,
                                          link_threshold=0,
                                          allowlist='0123456')
                    start_oppo = start_oppo + 42
                    score = res[0]
                    rounds_kills.append(score[0])
                    rounds_assists.append(score[1])
                except:
                    res = reader.readtext(img2, detail=0, text_threshold=0, threshold=0, link_threshold=0,
                                          allowlist='0123456')
                    start_oppo = start_oppo + 42
                    score = res[0]
                    rounds_kills.append(score[0])
                    rounds_assists.append(score[1])

        kills.append(rounds_kills)
        assists.append(rounds_assists)

    return kills, assists


def all_agents(image):
    agent_list = []

    st_u = 503
    gr_check = 161

    for i in range(5):

        b, g, r = image[st_u, gr_check]
        u = st_u

        while g < 100:
            u = u + 1
            b, g, r = image[u, gr_check]

        st_l = gr_check + 3
        _, new_g, _ = image[u, st_l]
        cur_img = image[u:u + 40, st_l:st_l + 40]
        st_u = u + 42

        agent_list.append(cur_img)

    st_u = 726

    for i in range(5):

        _, _, r = image[st_u, gr_check]
        u = st_u
        while r < 180:
            u = u + 1
            b, g, r = image[u, gr_check]

        st_l = gr_check + 3
        _, _, new_r = image[u, st_l]
        cur_img = image[u:u + 40, st_l:st_l + 40]
        st_u = u + 42

        agent_list.append(cur_img)

    return agent_list


def match_agent(agent_images, images, agents_names, timestamps):
    """This function matches all the agents kills and death sprites to their actual agent names and returns
    what agent got the kill and died for the first n engagements, usually 3."""

    round_agents = []

    for r, image in enumerate(images):

        indexes_fk = []
        indexes_dt = []

        agent_img = []
        agent_img_dt = []

        st_l = 945
        st_u = 500
        gr_check = 985

        st_l_dt = 1231

        for i in timestamps[r]:

            values_dt = []
            values = []

            b, g, r = image[st_u, gr_check]
            u = st_u

            while g < 100 and r < 100:
                u = u + 1
                b, g, r = image[u, gr_check]

            cur_img = image[u:u + 36, st_l:st_l + 36]
            cur_img_dt = image[u:u + 36, st_l_dt:st_l_dt + 36]

            agent_img.append(cur_img)
            agent_img_dt.append(cur_img_dt)

            st_u = u + 36
            for agent in agent_images:
                result = cv.matchTemplate(cur_img, agent, cv.TM_CCOEFF_NORMED)
                min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
                values.append(max_val)

                result_dt = cv.matchTemplate(cur_img_dt, agent, cv.TM_CCOEFF_NORMED)
                min_val_dt, max_val_dt, min_loc_dt, max_loc_dt = cv.minMaxLoc(result_dt)
                values_dt.append(max_val_dt)

            indexes_dt.append(values_dt.index(max(values_dt)))
            indexes_fk.append(values.index(max(values)))

        fk_player = [agents_names[index] for index in indexes_fk]
        fk_dt = [agents_names[index] for index in indexes_dt]

        round_agents.append(list(map(list, zip(fk_player, fk_dt))))

    first_eng_left = []
    sec_eng_left = []
    third_eng_left = []
    fourth_eng_left = []

    first_eng_right = []
    sec_eng_right = []
    third_eng_right = []
    fourth_eng_right = []

    for round_no, round_engagements in enumerate(round_agents):
        first_eng_left.append(round_engagements[0][0])
        sec_eng_left.append(round_engagements[1][0])
        third_eng_left.append(round_engagements[2][0])
        fourth_eng_left.append(round_engagements[3][0])
        first_eng_right.append(round_engagements[0][1])
        sec_eng_right.append(round_engagements[1][1])
        third_eng_right.append(round_engagements[2][1])
        fourth_eng_right.append(round_engagements[3][1])

    return first_eng_left, sec_eng_left, third_eng_left, fourth_eng_left, first_eng_right, sec_eng_right, third_eng_right, fourth_eng_right, round_agents


def map_player_agents(who_fb, fk_player, fk_dt, players_agents):

    players_agents_team = dict(list(players_agents.items())[:5])
    players_agents_oppo = dict(list(players_agents.items())[5:])
    players_agents_team = {value: key for key, value in players_agents_team.items()}
    players_agents_oppo = {value: key for key, value in players_agents_oppo.items()}
    print("Your team:", players_agents_team, "\n", "Opponent:", players_agents_oppo)

    final_player_fk_list = []
    final_opponent_dt_list = []

    for i, agent in enumerate(fk_player):

        if who_fb[i] == 'team':
            final_player_fk_list.append(players_agents_team.get(agent))
        else:
            final_player_fk_list.append(players_agents_oppo.get(agent))

    for i, agent in enumerate(fk_dt):

        if who_fb[i] == 'opponent':
            final_opponent_dt_list.append(players_agents_team.get(agent))
        else:
            final_opponent_dt_list.append(players_agents_oppo.get(agent))

    return final_player_fk_list, final_opponent_dt_list


FOLDER_PATH = os.path.join(os.getenv("LOCALAPPDATA"), "Viz app")



