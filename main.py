

# Internal Packages
from core.data_capture_module import capture

timeline_images, greens, who_fb, scoreboard_image, summary_image = capture.read_images_from_folder()

first_timeline_image = timeline_images[0] # changed the tl_ss and first tl image name

scoreboard_val = scoreboard_ocr(scoreboard_image)
players_agents, agents_names = zip_player_agents(first_timeline_image)
agents_sprites = all_agents(first_timeline_image)
timestamps, plants_or_not, buy_info_team, buy_info_oppo, awps = rounds_ocr(timeline_images)
outcomes = ocr_round_win(timeline_images)
map_info = get_metadata(first_timeline_image)  # first image only, changed
events_team, events_opp, event_sides = total_events(timeline_images)
site_list = bombsites_plants(timeline_images, map_info)
awp_information = awp_info(awps)
kills, assists = kill_ass_kast(timeline_images)
# TODO: Implement the main flow of the program, top level code I think.

spike_planted_boolean_all_rounds = [round_instance.__contains__('Planted') for round_instance in plants_or_not]
spike_defused_boolean_all_rounds = [round_instance.__contains__('Defused') for round_instance in plants_or_not]
first_event_is_plant_boolean_all_rounds = [round_instance[0].__contains__('Planted') for round_instance in plants_or_not]
second_event_is_plant_boolean_all_rounds = [round_instance[1].__contains__('Planted') for round_instance in plants_or_not]

rounds_first_bloods = get_first_bloods(timeline_images) # make into its own method
# for green in greens:
#     flag = 'team' if green > 100 else 'opponent'
#     who_fb.append(flag)
#
# for i in range(len(events_team)):
#     if plants[i] is True:
#
#         if sides[i] == 'Attack':
#             events_team[i] -= 1
#         else:
#             events_opp[i] -= 1
#
#     if defuses[i] is True:
#         if sides[i] == 'Defense':
#             events_team[i] -= 1
#         else:
#             events_opp[i] -= 1

(first_event_left_player, second_event_left_player, third_event_left_player, fourth_event_left_player, first_event_right_player, second_event_right_player, third_event_right_player,
 fourth_event_right_player, round_agents) = match_agent(agents_sprites, timeline_images, agents_names, timestamps)

all_rounds_data_formatted = generate_all_round_info(round_agents, event_sides, plants_or_not, timestamps)

all_rounds_anchor_times = calculate_all_rounds_anchor_times() # make into method
# anchor_times = []
#
# for r, round_instance in enumerate(all_rounds_data_formatted):
#
#     for event in round_instance:
#
#         if event == round_instance[-1]:
#             if event[-1] == "Kill":
#                 anchor_times.append(0)
#                 break
#
#         if event[-1] == "Spike":
#             anchor_times.append(event[2])
#             break
#
#         if event[-1] == "Kill":
#             continue


get_first_three_round_kill_data() # method

# fk_player = []
# fk_death = []
#
# sk_player = []
# sk_death = []
#
# tk_player = []
# tk_death = []
#
# for i, first_event_is_plant in enumerate(first_event_is_plant_boolean_all_rounds):
#
#     if not first_event_is_plant:
#         fk_player.append(first_event_left_player[i])
#         fk_death.append(first_event_right_player[i])
#
#         if not second_event_is_plant[i]:
#             sk_player.append(second_event_left_player[i])
#             sk_death.append(second_event_right_player[i])
#
#             tk_player.append(third_event_left_player[i])
#             tk_death.append(third_event_right_player[i])
#
#         else:
#             sk_player.append(third_event_left_player[i])
#             sk_death.append(third_event_right_player[i])
#
#             tk_player.append(fourth_event_left_player[i])
#             tk_death.append(fourth_event_right_player[i])
#
#     if first_event_is_plant:
#         fk_player.append(second_event_left_player[i])
#         fk_death.append(second_event_right_player[i])
#
#         sk_player.append(third_event_left_player[i])
#         sk_death.append(third_event_right_player[i])
#
#         tk_player.append(fourth_event_left_player[i])
#         tk_death.append(fourth_event_right_player[i])

check_true_fb_all_rounds() # method again

# true_fb = []
#
# for i in range(len(timestamps)):
#
#     if fk_player[i] == sk_death[i]:
#
#         if event_sides[i][0] != event_sides[i][1]:
#             true_fb.append(False)
#         else:
#             true_fb.append(True)
#
#     elif fk_player[i] == tk_death[i]:
#
#         first = timestamps[i][0]
#         second = timestamps[i][2]
#
#         if int(second) - int(first) <= 10:
#             true_fb.append(False)
#         else:
#             true_fb.append(True)
#
#     else:
#         true_fb.append(True)

first_kill_times, second_kill_times = first_and_second_kills(action_times, first_is_plant)
fbs_players, dt_players = map_player_agents(fb_team, fk_player, fk_death, players_agents)