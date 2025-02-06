import pprint
from datetime import datetime

import pandas

# Internal Packages
from core.data_capture_module import capture
from core.logger_module.logger import Logger
from core.processing_module import text_helpers as txt
from core.processing_module import image_helpers as img

Logger.info("Starting application")

timeline_images, scoreboard_image, summary_image = capture.read_images_from_folder()
first_timeline_image = timeline_images[0]

# Logger.save_logs(None)

total_rounds_no, sides_each_round, final_score = img.scores_ocr(summary_image)
scoreboard_val = img.scoreboard_ocr(scoreboard_image)
player_list, agent_list = img.get_player_and_agents_names(first_timeline_image)
player_agents_zipped = dict(zip(player_list, agent_list))
agents_sprites = img.get_agent_sprites(first_timeline_image)
timestamps, plants_or_not, buy_info_team, buy_info_oppo, awps = img.rounds_ocr(timeline_images)
outcomes = img.get_round_outcomes_all_rounds(timeline_images)
map_name = img.get_metadata(first_timeline_image)
events_team_counter_each_round, events_opponent_counter_each_round, list_of_sides_of_each_event_each_round = img.total_events(timeline_images)
spike_plant_site_list = img.bombsites_plants(timeline_images, map_name)
awp_information = txt.awp_info(awps)
kills, assists = txt.kill_ass_kast(timeline_images)
# TODO: Implement the main flow of the program, top level code I think.

spike_planted_boolean_all_rounds = [round_instance.__contains__('Planted') for round_instance in plants_or_not]
spike_defused_boolean_all_rounds = [round_instance.__contains__('Defused') for round_instance in plants_or_not]
first_event_is_plant_boolean_all_rounds = [round_instance[0].__contains__('Planted') for round_instance in plants_or_not]
second_event_is_plant_boolean_all_rounds = [round_instance[1].__contains__('Planted') for round_instance in plants_or_not]

first_bloods_team_each_round = txt.get_first_bloods_team_sides_each_round(timeline_images)
kills_opponent_counter_each_round, kills_team_counter_each_round = txt.update_kills_from_total_events_each_round(events_opponent_counter_each_round, events_team_counter_each_round, first_bloods_team_each_round, spike_planted_boolean_all_rounds, spike_defused_boolean_all_rounds, sides_each_round)

(first_event_left_player, second_event_left_player, third_event_left_player, fourth_event_left_player, first_event_right_player, second_event_right_player, third_event_right_player,
 fourth_event_right_player, round_agents) = img.match_agent(agents_sprites, timeline_images, agent_list, timestamps)

all_rounds_data_formatted = txt.generate_all_round_info(round_agents, list_of_sides_of_each_event_each_round, plants_or_not, timestamps)

all_rounds_anchor_times = txt.calculate_all_rounds_anchor_times(all_rounds_data_formatted) # make into method


fk_player, fk_death, sk_player, sk_death, tk_player, tk_death= txt.get_first_three_rounds_kill_data(first_event_is_plant_boolean_all_rounds, second_event_is_plant_boolean_all_rounds, first_event_left_player,
                                     second_event_left_player, third_event_left_player, fourth_event_left_player, first_event_right_player,
                                     second_event_right_player, third_event_right_player, fourth_event_right_player)

true_fb_each_round = txt.check_true_fb_all_rounds(timestamps, fk_player, fk_death, list_of_sides_of_each_event_each_round, tk_death) # method again


first_kill_times, second_kill_times = txt.first_and_second_kills(timestamps, first_event_is_plant_boolean_all_rounds)
fbs_players, dt_players = txt.map_player_agents(first_bloods_team_each_round, fk_player, fk_death, player_agents_zipped)

date = datetime.now()
dt_string = date.strftime("%d/%m/%Y")

data = {}
json_data = {}

lists = [timestamps, spike_planted_boolean_all_rounds, spike_defused_boolean_all_rounds, fk_player, fk_death, outcomes, first_bloods_team_each_round, awp_information, buy_info_team,
         buy_info_oppo, kills_team_counter_each_round, kills_opponent_counter_each_round, first_event_is_plant_boolean_all_rounds, sides_each_round, fbs_players, dt_players, first_kill_times,
         total_rounds_no, spike_plant_site_list, true_fb_each_round, final_score, map_name, dt_string, player_agents_zipped, all_rounds_anchor_times, all_rounds_data_formatted,
         kills, assists, scoreboard_val]

names = ["event_timestamps", "plants", "defuses", "fk_player", "fk_death", "outcomes", "fb_team", "awp_info",
         "buy_info_team", "buy_info_oppo", "kills_team", "kills_opp", "first_is_plant", "sides", "fbs_players",
         "dt_players", "first_kill_times", "rounds", "bombsites", "true_fb", "fscore", "map_name", "dt_string",
         "players_agents", "anchor_times", "round_events", "kills", "assists", "scoreboard"]

for name, lst in zip(names, lists):

    json_data[name] = lst

    excluded_headers = ["scoreboard", "event_timestamps", "kills", "assists"]
    if type(lst) == list and name not in excluded_headers:
        print(name, len(lst))
        data[name] = lst

# pprint.pprint(data)

df = pandas.DataFrame
df = df(data)

print(df.columns)
print(df.head(5))

df.to_csv("data.csv")

Logger.info("Data extraction complete.")

