import sys
import traceback
from datetime import datetime
import easyocr
import os
import requests

# Internal packages
from core.logger_module import logger
from core.data_capture_module import capture
from core.processing_module.image_helpers import match_agent

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


FOLDER_PATH = os.path.join(os.getenv("LOCALAPPDATA"), "Viz app")
