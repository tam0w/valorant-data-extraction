from datetime import datetime
import cv2 as cv
import easyocr
import numpy as np
import pandas as pd
import pyautogui as py
import time
import os
import keyboard
import matplotlib.pyplot as plt

# Load resources

reader = easyocr.Reader(['en'])
agents = pd.read_csv(r'D:\PROJECTS\demo-analysis-timeline\res\agentinfo.csv', header=0)
header = ['first_kill', 'time', 'first_death', 'planted', 'fb_team', 'defuse', 'fb_players', 'dt_players',
          'team_buy', 'oppo_buy', 'total_kills', 'total_deaths', 'awps_info', 'side', 'round_win']
username = os.getlogin()

# Functions


def analyze():
    """ This function will analyze the returned information from each individual round OCR and POST the
    final dataframe into the API endpoint? Or maybe this function will just give the final dataframe from the TL round
    analysis, into a json converting function which will then be posted into the website, perhaps."""

    df = pd.DataFrame(columns=header)

    (first_action_times, plants, defuses, fk_player, fk_death, outcomes, fb_team, players_agents, awp_info, fscore,
     buy_info_team, buy_info_oppo, map_name, kills_team, kills_opp, first_is_plant, sides, rounds) = rounds_ss()

    if not os.path.exists(rf'C:\Users\{username}\Desktop\scrims'):
        os.makedirs(rf'C:\Users\{username}\Desktop\scrims')

    df['side'] = sides[:rounds]
    df['round_win'] = outcomes
    df['first_kill'] = fk_player
    df['first_death'] = fk_death
    df['fb_team'] = fb_team
    df['team_buy'] = buy_info_team
    df['oppo_buy'] = buy_info_oppo
    df['planted'] = plants
    df['defuse'] = defuses
    df['total_kills'] = kills_team
    df['total_deaths'] = kills_opp
    df['awps_info'] = awp_info

    first_kill_times = []

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
    dt_string = date.strftime("%d_%m_%Y")

    df.to_csv(path_or_buf=rf'C:\Users\{username}\Desktop\scrims\{dt_string}_{map_name}_{fscore}.csv',
              sep='\t', header=header)
    print(df)


def rounds_ss():
    """ This function will go to the timeline page of the match in question and screenshot every page of the timeline.
    It will then run the OCR function for all the rounds in the match as specified and append them  to a list. This
    list will be returned to the 'analyze' function. """

    rounds, sides, fscore = scores_ocr()

    tl_ss = []
    greens = []
    who_fb = []

    while True:
        if keyboard.is_pressed('p'):
            image = py.screenshot()
            cv_image = cv.cvtColor(np.array(image), cv.COLOR_RGB2BGR)
            b, g, r = cv_image[520, 1150]
            greens.append(g)
            tl_ss.append(cv_image)
            print("Round screenshotted: ", len(tl_ss))
            time.sleep(0.3)

        if keyboard.is_pressed('q'):
            print('Timeline screenshotting complete.')
            break

    players_agents, agents_names = zip_player_agents()
    agent_list = all_agents(tl_ss)
    timestamps, plants_or_not, buy_info_team, buy_info_oppo, awps = rounds_ocr(tl_ss)
    fk_player, fk_death = match_agent(agent_list, tl_ss, agents_names)
    outcomes = ocr_round_win(tl_ss)
    map_info = get_metadata(tl_ss)
    events_team, events_opp = total_events(tl_ss)

    plants = [round_instance.__contains__('Planted') for round_instance in plants_or_not]
    defuses = [round_instance.__contains__('Defused') for round_instance in plants_or_not]
    first_is_plant = [round_instance[0].__contains__('Planted') for round_instance in plants_or_not]

    awp_info = []

    for awp in awps:
        indexes = [idx for idx, value in enumerate(awp) if value == 'Operator']

        if len(indexes) == 0:
            awp_info.append('none')
            continue
        if len(indexes) == 1:
            if indexes[0] < 11:
                awp_info.append('team')
                continue
            else:
                awp_info.append('opponent')
                continue
        if len(indexes) == 2:
            awp_info.append('both')

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

    return (timestamps, plants, defuses, fk_player, fk_death, outcomes, who_fb, players_agents, awp_info, fscore,
            buy_info_team, buy_info_oppo, map_info, events_team, events_opp, first_is_plant, sides, rounds)


def df_to_json():
    """Preferably take in the final dataframe and convert it into the JSON before POSTing into the API endpoint."""


def scores_ocr():
    """Any preprocessing or other shenanigans here. And then perform OCR and return match metadata, individual player
        stats as well as match score / outcome. This can be a data frame. Also, distinctly return total no of rounds."""
    time.sleep(2)
    sides = side_first_half()
    time.sleep(0.15)

    my_rounds, match_result, opp_rounds = final_score_ocr()
    fscore = my_rounds+" - "+opp_rounds
    print("Score:", fscore, "\nResult: ", match_result)
    total_rounds = int(my_rounds) + int(opp_rounds)

    return total_rounds, sides, fscore


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

    awp_or_no = [images[450:950, 650:785] for images in all_round_images]
    awps = [reader.readtext(image, detail=0) for image in awp_or_no]

    return timestamps, plants, buy_info_team, buy_info_oppo, awps


def all_agents(tl_ss):

    image = tl_ss[0]
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


def get_metadata(tl_ss):
    cv_image = tl_ss[0]
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
    print("Your team:", players_agents_team, "\n", "Opponent:", players_agents_oppo)

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


def total_events(tl_ss):

    """Total kills including plants and defuses."""

    events_team = []
    events_opp = []

    for pic in tl_ss:
        start = 510
        counter_opp = 0
        counter_team = 0
        while True:
            b1, g1, r1 = pic[start, 940]
            if g1 > 190 and b1 > 100:
                counter_team += 1
            if g1 < 100 and r1 > 200 and b1 < 100:
                counter_opp += 1
            if b1 < 100 and g1 < 100 and r1 < 100:
                events_team.append(counter_team)
                events_opp.append(counter_opp)
                break
            start += 38

    return events_team, events_opp


def bombsite(tl_ss, map_name):
    spike_p = r'D:\PROJECTS\demo-analysis-timeline\legacy\test1.png'
    spike = cv.imread(spike_p)
    # spike = cv.resize(spike,dsize=(15,15))
    plt.imshow(spike)
    plt.show

    for image in tl_ss:

        minimap = image[490:990, 1270:1770]
        resu = cv.matchTemplate(minimap, spike, cv.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(resu)

        if max_val > 70:

            if map_name == 'Bind':

            elif map_name == 'Ascent':

            elif map_name == 'Haven':

            elif map_name == 'Lotus':

            elif map_name == 'Pearl':

            elif map_name == 'Fracture':

            elif map_name == 'Split'

