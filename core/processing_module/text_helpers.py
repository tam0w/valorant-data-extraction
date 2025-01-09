from difflib import get_close_matches

from core.constants import list_of_agents
from core.logger_module.logger import Logger
from core.ocr_module.ocr import reader


def correct_agent_name(agent_name):
    closest_match = get_close_matches(agent_name, list_of_agents, n=1)
    if closest_match:
        return closest_match[0]
    else:
        return 0


def get_first_bloods_team_sides_each_round(timeline_images):
    first_bloods = []

    for image in timeline_images:
        b, g, r = image[520, 1150]

        flag = 'team' if g > 100 else 'opponent'
        first_bloods.append(flag)
    return first_bloods

def update_kills_from_total_events_each_round(events_opponent_counter_each_round, events_team_counter_each_round,
                                              first_bloods_team_each_round, plants, defuses, sides):
    kills_opponent_counter_each_round = events_opponent_counter_each_round
    kills_team_counter_each_round = events_team_counter_each_round
    Logger.warning(first_bloods_team_each_round)
    for i in range(len(first_bloods_team_each_round)):
        # loop over all the rounds and increment/decrement the number of events based on if there were plants and/or defuses to get the kills rather than events
        if plants[i] is True:

            if sides[i] == 'Attack':
                kills_team_counter_each_round[i] -= 1
            else:
                kills_opponent_counter_each_round[i] -= 1

        if defuses[i] is True:
            if sides[i] == 'Defense':
                kills_team_counter_each_round[i] -= 1
            else:
                kills_opponent_counter_each_round[i] -= 1

    return kills_opponent_counter_each_round, kills_team_counter_each_round


def calculate_all_rounds_anchor_times(all_rounds_data_formatted):
    anchor_times = []

    for r, round_instance in enumerate(all_rounds_data_formatted):

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

    return anchor_times

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


def get_first_three_rounds_kill_data(first_event_is_plant_boolean_all_rounds, second_event_is_plant_boolean_all_rounds, first_event_left_player,
                                     second_event_left_player, third_event_left_player, fourth_event_left_player,
                                     first_event_right_player,
                                     second_event_right_player, third_event_right_player, fourth_event_right_player):
    fk_player = []
    fk_death = []

    sk_player = []
    sk_death = []

    tk_player = []
    tk_death = []

    for i, first_event_is_plant in enumerate(first_event_is_plant_boolean_all_rounds):

        if not first_event_is_plant:
            fk_player.append(first_event_left_player[i])
            fk_death.append(first_event_right_player[i])

        if not second_event_is_plant_boolean_all_rounds[i]:
            sk_player.append(second_event_left_player[i])
            sk_death.append(second_event_right_player[i])

            tk_player.append(third_event_left_player[i])
            tk_death.append(third_event_right_player[i])

        else:
            sk_player.append(third_event_left_player[i])
            sk_death.append(third_event_right_player[i])

            tk_player.append(fourth_event_left_player[i])
            tk_death.append(fourth_event_right_player[i])

        if first_event_is_plant:
            fk_player.append(second_event_left_player[i])
            fk_death.append(second_event_right_player[i])

            sk_player.append(third_event_left_player[i])
            sk_death.append(third_event_right_player[i])

            tk_player.append(fourth_event_left_player[i])
            tk_death.append(fourth_event_right_player[i])

    return fk_player, fk_death, sk_player, sk_death, tk_player, tk_death


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


def check_true_fb_all_rounds(timestamps, fk_player, sk_death):
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

    return true_fb


def fix_times(timestamps):
    new_timestamps = []

    for i, round in enumerate(timestamps):

        new_round = []

        for timestamp in round:

            if timestamp.startswith('0'):

                timestamp = int(timestamp.replace('0:0', '').replace('0:', '').replace('.', '').replace(':', ''))
                new_round.append(timestamp)

            elif timestamp.startswith('N'):

                timestamp = 0
                new_round.append(timestamp)

            else:

                min = 60
                timestamp = timestamp.replace('1.', '').replace('1:', '').replace('.', '').replace(':', '').replace('T',
                                                                                                                    '').replace(
                    'l', '')
                timestamp = int(timestamp) + min
                new_round.append(timestamp)

        new_timestamps.append(new_round)

    return new_timestamps


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
