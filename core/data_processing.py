from difflib import get_close_matches
import numpy as np
from typing import List, Dict, Tuple, Optional, Any, cast
from datetime import datetime
from core.types import RoundData, MatchData, PlayerData, EventData, Position, ImageRegion
from core.constants import list_of_agents
from core.ocr import extract_text
from core.image_processing import crop_image, detect_color, get_team_color_from_pixel, detect_plant_site
from core.logger import logger


def normalize_agent_name(agent_name: str) -> str:
    """Correct agent name by finding the closest match"""
    closest_match = get_close_matches(agent_name, list_of_agents, n=1)
    if closest_match:
        return closest_match[0]
    else:
        # Ask for manual input as fallback
        corrected = input(f"Could not recognize agent '{agent_name}'. Please enter correct name: ")
        if corrected.lower() == 'kayo':
            return 'KAY/O'
        return corrected


def extract_player_data(image: np.ndarray) -> Tuple[List[str], List[str]]:
    """Extract player names and agent names from the scoreboard"""
    player_list = []
    agent_list = []

    # Process team players (top section)
    start_y = 495
    check_x = 200

    for i in range(5):
        y = start_y
        while detect_color(image, Position(y, check_x))[1] < 90:  # green < 90
            y += 1

        # Extract player name and agent
        player_region = crop_image(image, ImageRegion(y, y + 40, check_x + 3, check_x + 183))
        ocr_result = extract_text(player_region, detail=0, width_ths=25)

        if len(ocr_result) < 2:
            # Handle case where OCR didn't detect both player and agent
            if len(ocr_result) == 1:
                player_name = ocr_result[0]
                agent_name = input(f"Please confirm the agent {player_name} is playing: ").title()
            else:
                player_name = input(f"Please enter player name for position {i + 1}: ")
                agent_name = input(f"Please enter agent for {player_name}: ").title()
        else:
            player_name, agent_name = ocr_result[0], ocr_result[1]

        # Normalize agent name
        if agent_name not in list_of_agents:
            agent_name = normalize_agent_name(agent_name)

        player_list.append(player_name)
        agent_list.append(agent_name)
        start_y = y + 42

    # Process opponent players (bottom section)
    start_y = 726

    for i in range(5):
        y = start_y
        while detect_color(image, Position(y, check_x))[2] < 40:  # red < 40
            y += 1

        # Extract player name and agent
        player_region = crop_image(image, ImageRegion(y, y + 40, check_x + 3, check_x + 183))
        ocr_result = extract_text(player_region, detail=0, width_ths=25)

        if len(ocr_result) < 2:
            # Handle case where OCR didn't detect both player and agent
            if len(ocr_result) == 1:
                player_name = ocr_result[0]
                agent_name = input(f"Please confirm the agent {player_name} is playing: ").title()
            else:
                player_name = input(f"Please enter opponent player name for position {i + 1}: ")
                agent_name = input(f"Please enter agent for {player_name}: ").title()
        else:
            player_name, agent_name = ocr_result[0], ocr_result[1]

        # Normalize agent name
        if agent_name not in list_of_agents:
            agent_name = normalize_agent_name(agent_name)

        player_list.append(player_name)
        agent_list.append(agent_name)
        start_y = y + 42

    return player_list, agent_list


def extract_match_metadata(image: np.ndarray) -> Dict[str, Any]:
    """Extract map name, scores, and other metadata from summary screen"""
    # Extract sides (Attack/Defense)
    sides_region = crop_image(image, ImageRegion(300, 400, 1300, 1500))
    sides_text = extract_text(sides_region, detail=0)[0].lower()

    if 'def' in sides_text:
        first_half = "Defense"
        second_half = "Attack"
    else:
        first_half = "Attack"
        second_half = "Defense"

    sides = [first_half] * 12 + [second_half] * 12

    # Extract score
    score_region = crop_image(image, ImageRegion(70, 170, 700, 1150))
    score_parts = extract_text(score_region, detail=0)

    if len(score_parts) >= 3:
        team_score, result, opponent_score = score_parts[0:3]
    else:
        team_score = input("Please enter your team's score: ")
        opponent_score = input("Please enter opponent's score: ")
        result = "WIN" if int(team_score) > int(opponent_score) else "LOSS"

    # Extract map name
    map_region = crop_image(image, ImageRegion(125, 145, 120, 210))
    map_text = extract_text(map_region, detail=0)
    map_name = map_text[0].lower() if map_text else input("Please enter map name: ")

    return {
        'map_name': map_name,
        'team_score': team_score,
        'opponent_score': opponent_score,
        'result': result,
        'sides': sides,
        'total_rounds': int(team_score) + int(opponent_score),
        'final_score': f"{team_score} - {opponent_score}",
        'date': datetime.now().strftime("%d/%m/%Y")
    }


def extract_round_events(timeline_image: np.ndarray, agent_sprites: List[np.ndarray],
                         agent_list: List[str]) -> List[Tuple[str, str, int, str]]:
    """Extract events (kills, plants, defuses) from a round timeline"""
    events = []
    start_y = 500
    check_x = 940  # Position to check for event color
    kill_x = 945  # Position of killer agent icon
    death_x = 1231  # Position of death agent icon

    # Scan vertically for events
    current_y = start_y
    while current_y < 1060:
        # Check if there's an event at this position
        b, g, r = detect_color(timeline_image, Position(current_y, check_x))

        if g < 100 and r < 100 and b < 100:
            # No event, move down
            current_y += 1
            continue

        # Determine side (team/opponent)
        side = 'team' if g > 100 else 'opponent'

        # Extract timestamp
        timestamp_region = crop_image(timeline_image, ImageRegion(
            current_y, current_y + 36, 980, 1040))
        timestamp_text = extract_text(timestamp_region, detail=0)

        # Check if it's a plant/defuse
        event_type_region = crop_image(timeline_image, ImageRegion(
            current_y, current_y + 36, 1150, 1230))
        event_type_text = extract_text(event_type_region, detail=0)

        # Extract agent icons for kill events
        killer_icon = crop_image(timeline_image, ImageRegion(
            current_y, current_y + 36, kill_x, kill_x + 36))
        victim_icon = crop_image(timeline_image, ImageRegion(
            current_y, current_y + 36, death_x, death_x + 36))

        # Match agent icons to determine killer and victim
        killer_scores = []
        victim_scores = []

        for agent_sprite in agent_sprites:
            # Match killer
            killer_result = cv.matchTemplate(killer_icon, agent_sprite, cv.TM_CCOEFF_NORMED)
            _, killer_max_val, _, _ = cv.minMaxLoc(killer_result)
            killer_scores.append(killer_max_val)

            # Match victim
            victim_result = cv.matchTemplate(victim_icon, agent_sprite, cv.TM_CCOEFF_NORMED)
            _, victim_max_val, _, _ = cv.minMaxLoc(victim_result)
            victim_scores.append(victim_max_val)

        killer_idx = killer_scores.index(max(killer_scores))
        victim_idx = victim_scores.index(max(victim_scores))

        killer_agent = agent_list[killer_idx]
        victim_agent = agent_list[victim_idx]

        # Determine timestamp as integer
        timestamp = 0
        if timestamp_text:
            ts_text = timestamp_text[0]
            if ts_text.startswith('0'):
                # Format: 0:MM or 0:SS
                ts_text = ts_text.replace('0:0', '').replace('0:', '').replace('.', '').replace(':', '')
                timestamp = int(ts_text) if ts_text.isdigit() else 0
            elif ts_text.startswith('1'):
                # Format: 1:MM or 1:SS (add 60 seconds)
                ts_text = ts_text.replace('1.', '').replace('1:', '').replace('.', '').replace(':', '')
                timestamp = int(ts_text) + 60 if ts_text.isdigit() else 60

        # Determine event type
        if event_type_text and any('Plant' in t for t in event_type_text):
            event_type = 'plant'
        elif event_type_text and any('Defuse' in t for t in event_type_text):
            event_type = 'defuse'
        else:
            event_type = 'kill'

        events.append((killer_agent, victim_agent, timestamp, event_type))

        # Move to next event
        current_y += 36

    return events


def normalize_timestamps(timestamps: List[str]) -> List[int]:
    """Convert timestamp strings to normalized integers"""
    normalized = []

    for timestamp in timestamps:
        if timestamp.startswith('0'):
            # Format: 0:MM or 0:SS
            ts = timestamp.replace('0:0', '').replace('0:', '').replace('.', '').replace(':', '')
            normalized.append(int(ts) if ts.isdigit() else 0)
        elif timestamp.startswith('N'):
            normalized.append(0)
        else:
            # Format: 1:MM or 1:SS (add 60 seconds)
            ts = timestamp.replace('1.', '').replace('1:', '').replace('.', '').replace(':', '').replace('T',
                                                                                                         '').replace(
                'l', '')
            normalized.append(int(ts) + 60 if ts.isdigit() else 60)

    return normalized


def extract_first_bloods(timeline_images: List[np.ndarray]) -> List[str]:
    """Determine which team got first blood in each round"""
    first_bloods = []

    for image in timeline_images:
        # Check pixel color at first blood position
        b, g, r = detect_color(image, Position(520, 1150))

        # Green indicates team got first blood, otherwise opponent
        team = 'team' if g > 100 else 'opponent'
        first_bloods.append(team)

    return first_bloods


def determine_awp_info(awp_data: List[List[str]]) -> List[str]:
    """Determine AWP (Operator) usage in each round"""
    awp_info = []

    for round_awp in awp_data:
        # Find indices of "Operator" strings
        indices = [i for i, val in enumerate(round_awp) if val == 'Operator']

        if not indices:
            awp_info.append('none')
        elif len(indices) == 1:
            # Single AWP - determine if team or opponent
            awp_info.append('team' if indices[0] < 11 else 'opponent')
        elif len(indices) == 2:
            # Two AWPs - determine if same team or both teams
            if all(idx < 11 for idx in indices):
                awp_info.append('team')
            elif all(idx >= 11 for idx in indices):
                awp_info.append('opponent')
            else:
                awp_info.append('both')
        else:
            # More than two AWPs
            awp_info.append('both')

    return awp_info


def process_round_outcomes(timeline_images: List[np.ndarray]) -> List[str]:
    """Determine if each round was a win or loss"""
    outcomes = []

    for image in timeline_images:
        outcome_region = crop_image(image, ImageRegion(430, 470, 130, 700))
        outcome_text = extract_text(outcome_region, detail=0)

        # Check if "LOSS" appears in the text
        is_loss = any('LOSS' in t.upper() for t in outcome_text)
        outcomes.append('loss' if is_loss else 'win')

    return outcomes


def create_match_data(
        timeline_images: List[np.ndarray],
        scoreboard_image: np.ndarray,
        summary_image: np.ndarray
) -> MatchData:
    """Create a complete match data structure from screenshots"""
    # Extract basic metadata
    metadata = extract_match_metadata(summary_image)

    # Extract player and agent information
    player_list, agent_list = extract_player_data(timeline_images[0])
    players_agents = dict(zip(player_list, agent_list))

    # Extract agent sprites for event matching
    agent_sprites = extract_agent_sprites(timeline_images[0])

    # Process round outcomes
    outcomes = process_round_outcomes(timeline_images)

    # Determine first bloods
    first_bloods = extract_first_bloods(timeline_images)

    # Extract round timestamps and events
    round_events = []
    for image in timeline_images:
        events = extract_round_events(image, agent_sprites, agent_list)
        round_events.append(events)

    # Process economy and other round data
    economy_regions = [crop_image(img, ImageRegion(425, 480, 1020, 1145)) for img in timeline_images]
    economy_data = [extract_text(region, detail=0) for region in economy_regions]
    team_economy = [eco[0] if eco else "0" for eco in economy_data]
    opponent_economy = [eco[1] if len(eco) > 1 else "0" for eco in economy_data]

    # Extract AWP information
    awp_regions = [crop_image(img, ImageRegion(450, 950, 650, 785)) for img in timeline_images]
    awp_data = [extract_text(region, detail=0) for region in awp_regions]
    awp_info = determine_awp_info(awp_data)

    # Extract plant information
    plant_site_list = [detect_plant_site(img, metadata['map_name']) for img in timeline_images]

    # Create round data
    rounds = []
    for i in range(len(timeline_images)):
        if i >= len(outcomes) or i >= len(first_bloods):
            continue

        # Determine if spike was planted/defused
        has_plant = False
        has_defuse = False
        for _, _, _, event_type in round_events[i]:
            if event_type == 'plant':
                has_plant = True
            elif event_type == 'defuse':
                has_defuse = True

        # Calculate kills for each team
        team_kills = 0
        opponent_kills = 0
        for killer, victim, _, event_type in round_events[i]:
            if event_type == 'kill':
                killer_idx = agent_list.index(killer) if killer in agent_list else -1
                if 0 <= killer_idx < 5:  # Team player
                    team_kills += 1
                elif 5 <= killer_idx < 10:  # Opponent player
                    opponent_kills += 1

        # Adjust for plants/defuses which are also counted as events
        side = metadata['sides'][i] if i < len(metadata['sides']) else "Unknown"
        if has_plant:
            if side == 'Attack':
                team_kills -= 1
            else:
                opponent_kills -= 1

        if has_defuse:
            if side == 'Defense':
                team_kills -= 1
            else:
                opponent_kills -= 1

        # Create the round data
        round_data: RoundData = {
            'round_number': i + 1,
            'events': [],  # Will fill this later
            'outcome': outcomes[i],
            'side': side,
            'team_economy': team_economy[i] if i < len(team_economy) else "0",
            'opponent_economy': opponent_economy[i] if i < len(opponent_economy) else "0",
            'first_blood': first_bloods[i] if i < len(first_bloods) else "unknown",
            'true_first_blood': True,  # Simplified for now
            'first_blood_player': "",  # Will fill this later
            'first_death_player': "",  # Will fill this later
            'site': plant_site_list[i] if i < len(plant_site_list) and plant_site_list[i] else None,
            'plant': has_plant,
            'defuse': has_defuse,
            'awp_info': awp_info[i] if i < len(awp_info) else "none",
            'kills_team': team_kills,
            'kills_opponent': opponent_kills
        }

        rounds.append(round_data)

    # Generate unique match ID
    match_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    match_id = f"M_{metadata['map_name']}_{match_time}"

    # Create complete match data
    match_data: MatchData = {
        'id': match_id,
        'map_name': metadata['map_name'],
        'date': metadata['date'],
        'players_agents': players_agents,
        'final_score': metadata['final_score'],
        'rounds': rounds,
        'total_rounds': metadata['total_rounds']
    }

    return match_data