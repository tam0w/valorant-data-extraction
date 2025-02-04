import os

import cv2 as cv
import matplotlib.pyplot as plt
import numpy

from core.constants import list_of_agents
from core.logger_module.logger import Logger
from core.ocr_module.ocr import reader
from core.processing_module.text_helpers import correct_agent_name, fix_times


def side_first_half(cv_image):
    """Determines the side of the team in the first half of the game"""

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


def total_events(tl_ss):
    """Total events including plants and defuses. Number of events per """

    events_team_counter_each_round = []
    events_opponent_counter_each_round = []
    list_of_sides_of_each_event_all_rounds = []

    for pic in tl_ss:

        start = 510
        counter_opp = 0
        counter_team = 0
        specific_round_events = []

        while True:
            b1, g1, r1 = pic[start, 940]
            if g1 > 190 and b1 > 100:
                counter_team += 1
                specific_round_events.append('team')
            if g1 < 100 and r1 > 200 and b1 < 100:
                counter_opp += 1
                specific_round_events.append('opponent')
            if b1 < 100 and g1 < 100 and r1 < 100:
                events_team_counter_each_round.append(counter_team)
                events_opponent_counter_each_round.append(counter_opp)
                list_of_sides_of_each_event_all_rounds.append(specific_round_events)
                break
            start += 38

    return events_team_counter_each_round, events_opponent_counter_each_round, list_of_sides_of_each_event_all_rounds

def bombsites_plants(tl_ss, map_name):
    spike_p = os.path.join(os.getcwd(), "spike.png")
    spike = cv.imread(spike_p)

    sites = []

    for image in tl_ss:

        minimap = image[490:990, 1270:1770]
        resu = cv.matchTemplate(minimap, spike, cv.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(resu)
        x, y = max_loc

        if max_val > 0.70:

            if map_name == 'bind':
                site = 'B' if x < 250 else 'A'

            elif map_name == 'ascent':
                site = 'B' if y < 250 else 'A'

            elif map_name == 'haven':
                if y < 150:
                    site = 'A'
                elif 150 < y < 280:
                    site = 'B'
                else:
                    site = 'C'

            elif map_name == 'lotus':
                if x < 150:
                    site = 'C'
                elif 150 < x < 300:
                    site = 'B'
                else:
                    site = 'A'

            elif map_name == 'pearl':
                if x < 250 and 90 < y < 210:
                    site = 'B'
                if x > 250 and 90 < y < 210:
                    site = 'A'

            elif map_name == 'fracture':
                if x > 250 and 190 < y < 290:
                    site = 'A'
                if x < 250 and 190 < y < 290:
                    site = 'B'

            elif map_name == 'split':
                site = 'B' if y > 250 else 'A'

            elif map_name == 'sunset':
                site = 'A' if x > 250 else 'B'

            elif map_name == 'breeze':
                site = 'A' if x > 250 else 'B'

            elif map_name == 'icebox':
                site = 'A' if y > 200 else 'B'

            else:
                site = 'unclear'

            sites.append(site)

        else:

            sites.append("False")

    return sites

def get_player_and_agents_names(image):

    agent_list = []
    player_list = []

    st_u = 495
    gr_check = 200

    for i in range(5):

        b, g, r = image[st_u, gr_check]
        u = st_u

        while g < 90:
            u = u + 1
            b, g, r = image[u, gr_check]

        st_l = gr_check + 3
        _, new_g, _ = image[u, st_l]
        cur_img = image[u:u + 40, st_l:st_l + 180]
        st_u = u + 42

        res = reader.readtext(cur_img, detail=0, width_ths=25)

        if len(res) < 2:
            res.append(input(f'Please confirm the agent {res[0]} is playing:').title())
            if res[1].lower() == 'kayo':
                res[1] = 'KAY/O'

        if res[1] not in list_of_agents:

            res[1] = correct_agent_name(res[1])
            if res[1] == 0:
                res[1] = input(f'Please confirm the agent {res[0]} is playing:').title()
                if res[1].lower() == 'kayo':
                    res[1] = 'KAY/O'

        agent_list.append(res[1])
        player_list.append(res[0])

    st_u = 726

    for i in range(5):

        b, g, r = image[st_u, gr_check]
        u = st_u

        while r < 40:
            u = u + 1
            b, g, r = image[u, gr_check]

        st_l = gr_check + 3
        _, _, new_r = image[u, st_l]
        cur_img = image[u:u + 40, st_l:st_l + 180]
        st_u = u + 42

        res = reader.readtext(cur_img, detail=0, width_ths=25)

        if len(res) < 2:
            res.append(input(f'Please confirm the agent {res[0]} is playing:').title())
            if res[1].lower() == 'kayo':
                res[1] = 'KAY/O'

        if res[1] not in list_of_agents:

            res[1] = correct_agent_name(res[1])
            if res[1] == 0:
                res[1] = input(f'Please confirm the agent {res[0]} is playing:').title()
                if res[1].lower() == 'kayo':
                    res[1] = 'KAY/O'

        agent_list.append(res[1])
        player_list.append(res[0])

    return player_list, agent_list


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

def  scoreboard_ocr(img):
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

def final_score_ocr(cv_image):
    score = cv_image[70:170, 700:1150]
    # score1 = plt.imread(score)
    # plt.imshow(score1)
    score = reader.readtext(score, detail=0)
    print(score)

    return score[0].__str__(), score[1].__str__(), score[2].__str__()

def get_agent_sprites(image):

    """This function will extract the agent sprites from the image and return a list of the sprites for each agent."""
    agent_sprites_list = []

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

        agent_sprites_list.append(cur_img)

    st_u = 724

    for i in range(5):

        _, _, r = image[st_u, gr_check]
        u = st_u
        while r < 80:
            u = u + 1
            b, g, r = image[u, gr_check]

        st_l = gr_check + 3
        _, _, new_r = image[u, st_l]
        cur_img = image[u:u + 40, st_l:st_l + 40]
        st_u = u + 42

        agent_sprites_list.append(cur_img)

    return agent_sprites_list

# TODO: The way I'm currently working is that I do everything for every round at once, should I break this down to round stuff?
def rounds_ocr(all_round_images):
    """
    Perform OCR and preprocessing of all the rounds to extract information such as:
    - Which player got the first kill
    - When they got it
    - If the spike was planted or not

    Args:
        all_round_images (list): List of images for all rounds.

    Returns:
        tuple: Contains the following elements:
            - timestamps (list): List of timestamps for each round.
            - plants (list): List indicating if the spike was planted for each round.
            - buy_info_team (list): List of buy information for the team.
            - buy_info_oppo (list): List of buy information for the opponent.
            - awps (list): List indicating if an AWP was used in each round.
    """

    buys = [images[425:480, 1020:1145] for images in all_round_images]
    buy_info = [reader.readtext(image, allowlist=['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', ','], detail=0) for
                image in buys]
    buy_info_team = [buy[0] for buy in buy_info]
    buy_info_oppo = [buy[1] for buy in buy_info]

    all_round_images_cropped = [images[505:970, 980:1040] for images in all_round_images]
    timestamps_old = [reader.readtext(image, detail=0) for image in all_round_images_cropped]

    all_round_images_cropped_plants = [images[505:970, 1150:1230] for images in all_round_images]
    plants = [reader.readtext(image, detail=0) for image in all_round_images_cropped_plants]

    awp_or_no = [images[450:950, 650:785] for images in all_round_images]

    awps = [reader.readtext(image, detail=0) for image in awp_or_no]

    timestamps = fix_times(timestamps_old)

    return timestamps, plants, buy_info_team, buy_info_oppo, awps

def get_round_outcomes_all_rounds(images):
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

def get_metadata(first_timeline_image):
    file = first_timeline_image[125:145, 120:210]
    gray = cv.cvtColor(file, cv.COLOR_BGR2GRAY)
    gray = cv.convertScaleAbs(gray, 1, 5)
    result = reader.readtext(gray, detail=0)
    return result[0].__str__().lower()


def match_agent(agent_sprites, timeline_images, agents_names_list, timestamps):
    """This function matches all the agents kills and death sprites to their actual agent names and returns
    what agent got the kill and died for the first n engagements, usually 3."""

    round_agents = []

    for r, image in enumerate(timeline_images):

        print("round number:", r, "event list:", timestamps[r])

        plt.imshow(image)
        plt.show()

        indexes_fk = []
        indexes_dt = []

        agent_img = []
        agent_img_dt = []

        st_l = 945
        st_u = 500
        gr_check = 985

        st_l_dt = 1231

        for i in timestamps[r]:
            # for some fucking reason this only captures team playes i ams so lostttttttttttttt
            print("event:", i)

            similarity_scores_deaths = []
            similarity_scores_kills = []

            r, g, b = image[st_u, gr_check]
            u = st_u

            while g < 100 and r < 100:

                u = u + 1
                b, g, r = image[u, gr_check]

                if u > 900:
                    break
            if u > 900:
                break

            cur_img = image[u:u + 36, st_l:st_l + 36]
            cur_img_dt = image[u:u + 36, st_l_dt:st_l_dt + 36]

            plt.imshow(cur_img)
            plt.show()
            # plt.imshow(cur_img_dt)
            # plt.show()

            agent_img.append(cur_img)
            agent_img_dt.append(cur_img_dt)

            st_u = u + 36
            for agent in agent_sprites:
                result = cv.matchTemplate(cur_img, agent, cv.TM_CCOEFF_NORMED)
                min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
                similarity_scores_kills.append(max_val)

                result_dt = cv.matchTemplate(cur_img_dt, agent, cv.TM_CCOEFF_NORMED)
                min_val_dt, max_val_dt, min_loc_dt, max_loc_dt = cv.minMaxLoc(result_dt)
                similarity_scores_deaths.append(max_val_dt)

            # the index of the agent that died or killed based on the highest similarity score
            indexes_dt.append(similarity_scores_deaths.index(max(similarity_scores_deaths)))
            indexes_fk.append(similarity_scores_kills.index(max(similarity_scores_kills)))

            print("fk:", agents_names_list[similarity_scores_kills.index(max(similarity_scores_kills))], "dt:", agents_names_list[similarity_scores_deaths.index(max(similarity_scores_deaths))])

        # all the agents killed and dead in a given round (by us, its only recording our kills rn)
        kills_agents_names = [agents_names_list[index] for index in indexes_fk]
        deaths_agents_names = [agents_names_list[index] for index in indexes_dt]

        round_agents.append(list(map(list, zip(kills_agents_names, deaths_agents_names))))

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
