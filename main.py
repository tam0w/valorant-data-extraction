

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
events_team_counter_each_round, events_opponent_counter_each_round, list_of_sides_of_each_event_each_round = total_events(timeline_images)
site_list = bombsites_plants(timeline_images, map_info)
awp_information = awp_info(awps)
kills, assists = kill_ass_kast(timeline_images)
# TODO: Implement the main flow of the program, top level code I think.

spike_planted_boolean_all_rounds = [round_instance.__contains__('Planted') for round_instance in plants_or_not]
spike_defused_boolean_all_rounds = [round_instance.__contains__('Defused') for round_instance in plants_or_not]
first_event_is_plant_boolean_all_rounds = [round_instance[0].__contains__('Planted') for round_instance in plants_or_not]
second_event_is_plant_boolean_all_rounds = [round_instance[1].__contains__('Planted') for round_instance in plants_or_not]

first_bloods_team_each_round = get_first_bloods(timeline_images) # make into its own method

kills_opponent_counter_each_round, kills_team_counter_each_round = update_kills_from_total_events_each_round(events_opponent_counter_each_round, events_team_counter_each_round)

(first_event_left_player, second_event_left_player, third_event_left_player, fourth_event_left_player, first_event_right_player, second_event_right_player, third_event_right_player,
 fourth_event_right_player, round_agents) = match_agent(agents_sprites, timeline_images, agents_names, timestamps)

all_rounds_data_formatted = generate_all_round_info(round_agents, list_of_sides_of_each_event_each_round, plants_or_not, timestamps)

all_rounds_anchor_times = calculate_all_rounds_anchor_times(all_rounds_data_formatted) # make into method


fk_player, fk_death, sk_player, sk_death, tk_player, tk_death= get_first_three_round_kill_data(first_event_is_plant_boolean_all_rounds, first_event_left_player,
                                     second_event_left_player, third_event_left_player,  first_event_right_player,
                                     second_event_right_player, third_event_right_player)

true_fb_each_round = check_true_fb_all_rounds(timestamps, fk_player, fk_death) # method again


first_kill_times, second_kill_times = first_and_second_kills(action_times, first_is_plant)
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