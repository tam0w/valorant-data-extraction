from difflib import get_close_matches
from core.constants import list_of_agents
from core.logger_module.logger import Logger
from core.ocr_module.ocr import reader

def correct_agent_name(agent_name):
    """
    Corrects the agent name by finding the closest match from a predefined list of agents.

    Args:
        agent_name (str): The name of the agent to be corrected.

    Returns:
        str: The closest matching agent name or 0 if no match is found.
    """
    closest_match = get_close_matches(agent_name, list_of_agents, n=1)
    if closest_match:
        return closest_match[0]
    else:
        return 0

def get_first_bloods_team_sides_each_round(timeline_images):
    """
    Determines the team sides for first bloods in each round based on timeline images.

    Args:
        timeline_images (list): List of images representing the timeline of each round.

    Returns:
        list: A list indicating the team ('team' or 'opponent') for each first blood.
    """
    first_bloods = []

    for image in timeline_images:
        b, g, r = image[520, 1150]

        flag = 'team' if g > 100 else 'opponent'
        first_bloods.append(flag)
    return first_bloods

def update_kills_from_total_events_each_round(events_opponent_counter_each_round, events_team_counter_each_round,
                                              first_bloods_team_each_round, plants, defuses, sides):
    """
    Updates the kill counts for each round based on events, plants, and defuses.

    Args:
        events_opponent_counter_each_round (list): List of event counts for the opponent team for each round.
        events_team_counter_each_round (list): List of event counts for the player's team for each round.
        first_bloods_team_each_round (list): List indicating the team for each first blood in each round.
        plants (list): List indicating if a plant occurred in each round.
        defuses (list): List indicating if a defuse occurred in each round.
        sides (list): List indicating the side ('Attack' or 'Defense') for each round.

    Returns:
        tuple: Updated kill counts for the opponent and player's team for each round.
    """

    kills_opponent_counter_each_round = events_opponent_counter_each_round
    kills_team_counter_each_round = events_team_counter_each_round

    for i in range(len(first_bloods_team_each_round)):

        Logger.info(f"Round {i + 1} - First blood: {first_bloods_team_each_round[i]} Events [Team/Opp]: {events_team_counter_each_round[i], events_opponent_counter_each_round[i]}")

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
    """
    Calculates the anchor times for all rounds based on formatted round data.

    Args:
        all_rounds_data_formatted (list): List of formatted data for all rounds.

    Returns:
        list: List of anchor times for each round.
    """
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

def generate_all_round_info(round_engagements_agents, list_of_sides_of_each_event_each_round, plants_or_not, timestamps):
    """
    Generates information for all rounds including engagements, sides, plants, and timestamps.

    Args:
        round_engagements_agents (list): List of engagements for each round.
        list_of_sides_of_each_event_each_round (list): List of sides for each event in each round.
        plants_or_not (list): List indicating if a plant occurred for each event in each round.
        timestamps (list): List of timestamps for each event in each round.

    Returns:
        list: Updated list of engagements with additional information for each round.
    """
    rounds_engagements_events_data = round_engagements_agents

    for r, round_instance in enumerate(rounds_engagements_events_data):
        for i, timestamp in enumerate(timestamps[r]):
            round_instance[i].append(timestamp)
            round_instance[i].append(list_of_sides_of_each_event_each_round[r][i])
            try:
                if plants_or_not[r][i] == "Planted" or plants_or_not[r][i] == "Defused":
                    round_instance[i].append('Spike')
                else:
                    round_instance[i].append('Kill')
            except IndexError:
                round_instance[i].append('Kill')

    return rounds_engagements_events_data

def get_first_three_rounds_kill_data(first_event_is_plant_boolean_all_rounds, second_event_is_plant_boolean_all_rounds, first_event_left_player,
                                     second_event_left_player, third_event_left_player, fourth_event_left_player,
                                     first_event_right_player, second_event_right_player, third_event_right_player, fourth_event_right_player):
    """
    Retrieves kill data for the first three rounds based on event information.

    Args:
        first_event_is_plant_boolean_all_rounds (list): List indicating if the first event is a plant for all rounds.
        second_event_is_plant_boolean_all_rounds (list): List indicating if the second event is a plant for all rounds.
        first_event_left_player (list): List of left player for the first event in each round.
        second_event_left_player (list): List of left player for the second event in each round.
        third_event_left_player (list): List of left player for the third event in each round.
        fourth_event_left_player (list): List of left player for the fourth event in each round.
        first_event_right_player (list): List of right player for the first event in each round.
        second_event_right_player (list): List of right player for the second event in each round.
        third_event_right_player (list): List of right player for the third event in each round.
        fourth_event_right_player (list): List of right player for the fourth event in each round.

    Returns:
        tuple: Lists of players and deaths for the first, second, and third kills in each round.
    """
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
    """
    Retrieves the times for the first and second kills in each round.

    Args:
        action_times (list): List of action times for each round.
        first_is_plant (list): List indicating if the first event is a plant for each round.

    Returns:
        tuple: Lists of times for the first and second kills in each round.
    """
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
    """
    Maps player agents to their respective teams based on first blood information.

    Args:
        who_fb (list): List indicating the team for each first blood.
        fk_player (list): List of players for the first kills.
        fk_dt (list): List of deaths for the first kills.
        players_agents (dict): Dictionary mapping players to their agents.

    Returns:
        tuple: Lists of mapped player agents for first kills and deaths.
    """
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

def check_true_fb_all_rounds(timestamps, fk_player, sk_death, event_sides, tk_death):
    """
    Checks if the first bloods are true for all rounds based on timestamps and event sides.

    Args:
        timestamps (list): List of timestamps for each event in each round.
        fk_player (list): List of players for the first kills.
        sk_death (list): List of deaths for the second kills.
        event_sides (list): List of sides for each event in each round.
        tk_death (list): List of deaths for the third kills.

    Returns:
        list: List indicating if the first bloods are true for each round.
    """
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
    """
    Fixes the timestamps for each round by converting them to integers.

    Args:
        timestamps (list): List of timestamps for each event in each round.

    Returns:
        list: List of fixed timestamps for each round.
    """
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
                timestamp = timestamp.replace('1.', '').replace('1:', '').replace('.', '').replace(':', '').replace('T', '').replace('l', '')
                timestamp = int(timestamp) + min
                new_round.append(timestamp)

        new_timestamps.append(new_round)

    return new_timestamps

def awp_info(awps):
    """
    Retrieves information about AWP (Operator) usage in each round.

    Args:
        awps (list): List of AWP usage data for each round.

    Returns:
        list: List indicating the AWP usage ('none', 'team', 'opponent', or 'both') for each round.
    """
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
    """
    Retrieves kill and assist data for each round based on images.

    Args:
        images (list): List of images representing the kill and assist data for each round.

    Returns:
        tuple: Lists of kills and assists for each round.
    """
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
                    res = reader.readtext(img1, mag_ratio=2.2, detail=0, text_threshold=0, threshold=0, link_threshold=0, allowlist='0123456')
                    start = start + 42

                    score = res[0]
                    rounds_kills.append(score[0])
                    rounds_assists.append(score[1])
                except:
                    res = reader.readtext(img1, detail=0, text_threshold=0, threshold=0, link_threshold=0, allowlist='0123456')
                    start = start + 42

                    score = res[0]
                    rounds_kills.append(score[0])
                    rounds_assists.append(score[1])
            else:
                img2 = img[start_oppo:start_oppo + 38, 450:590]

                try:
                    res = reader.readtext(img2, mag_ratio=2.2, detail=0, text_threshold=0, threshold=0, link_threshold=0, allowlist='0123456')
                    start_oppo = start_oppo + 42
                    score = res[0]
                    rounds_kills.append(score[0])
                    rounds_assists.append(score[1])
                except:
                    res = reader.readtext(img2, detail=0, text_threshold=0, threshold=0, link_threshold=0, allowlist='0123456')
                    start_oppo = start_oppo + 42
                    score = res[0]
                    rounds_kills.append(score[0])
                    rounds_assists.append(score[1])

        kills.append(rounds_kills)
        assists.append(rounds_assists)

    return kills, assists