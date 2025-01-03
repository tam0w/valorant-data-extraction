def correct_agent_name(agent_name):
    closest_match = get_close_matches(agent_name, list_of_agents, n=1)
    if closest_match:
        return closest_match[0]
    else:
        return 0

def get_first_bloods(timeline_images):

    first_bloods = []

    for image in timeline_images:

        b, g, r = image[520, 1150]

        flag = 'team' if g > 100 else 'opponent'
        first_bloods.append(flag)

def update_kills_from_total_events_each_round(events_opponent_counter_each_round, events_team_counter_each_round):

    kills_opponent_counter_each_round = events_opponent_counter_each_round
    kills_team_counter_each_round = events_team_counter_each_round

    for i in range(len(rounds_first_bloods)):
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

def get_first_three_rounds_kill_data(first_event_is_plant_boolean_all_rounds, first_event_left_player,
                                     second_event_left_player, third_event_left_player, fourth_event_left_player, first_event_right_player,
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

        if not second_event_is_plant[i]:
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