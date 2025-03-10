import os
import json
import csv
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

from core.types import MatchData, RoundData


def generate_match_id(match_data: MatchData) -> str:
    """Generate unique match ID with M prefix"""
    # Create a hash of map name and timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    map_name = match_data['map_name']

    # Create a unique identifier using map name, score and timestamp
    match_str = f"{map_name}_{match_data['final_score']}_{timestamp}"
    match_hash = hashlib.md5(match_str.encode()).hexdigest()[:8]

    return f"M_{map_name}_{match_hash}"


def match_to_csv(match_data: MatchData, output_dir: str) -> str:
    """Convert match data to CSV format and save to file"""
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Generate filename
    map_name = match_data['map_name']
    score = match_data['final_score']
    date = match_data['date'].replace('/', '-')
    filename = f"data_{map_name}_{score}_{date}.csv"
    filepath = os.path.join(output_dir, filename)

    # Prepare data for CSV
    rows = []
    for round_data in match_data['rounds']:
        row = {
            'round_number': round_data['round_number'],
            'outcome': round_data['outcome'],
            'side': round_data['side'],
            'team_economy': round_data['team_economy'],
            'opponent_economy': round_data['opponent_economy'],
            'first_blood': round_data['first_blood'],
            'true_first_blood': round_data['true_first_blood'],
            'first_blood_player': round_data['first_blood_player'],
            'first_death_player': round_data['first_death_player'],
            'site': round_data['site'] if round_data['site'] else 'None',
            'plant': round_data['plant'],
            'defuse': round_data['defuse'],
            'awp_info': round_data['awp_info'],
            'kills_team': round_data['kills_team'],
            'kills_opponent': round_data['kills_opponent']
        }
        rows.append(row)

    # Write to CSV
    with open(filepath, 'w', newline='') as csvfile:
        if rows:
            writer = csv.DictWriter(csvfile, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)

    return filepath


def match_to_json(match_data: MatchData, output_dir: str) -> str:
    """Convert match data to JSON format and save to file"""
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Generate filename
    map_name = match_data['map_name']
    score = match_data['final_score']
    date = match_data['date'].replace('/', '-')
    filename = f"data_{map_name}_{score}_{date}.json"
    filepath = os.path.join(output_dir, filename)

    # Write to JSON
    with open(filepath, 'w') as jsonfile:
        json.dump(match_data, jsonfile, indent=4)

    return filepath