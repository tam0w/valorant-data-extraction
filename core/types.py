from typing import TypedDict, List, Dict, Optional, Tuple, NamedTuple, Union, Any
import numpy as np
from datetime import datetime


class ImageRegion(NamedTuple):
    y_start: int
    y_end: int
    x_start: int
    x_end: int


class Position(NamedTuple):
    y: int
    x: int


class PlayerData(TypedDict):
    name: str
    agent: str
    team: str  # 'team' or 'opponent'
    kills: int
    deaths: int
    assists: int


class EventData(TypedDict):
    timestamp: int
    event_type: str  # 'kill', 'plant', 'defuse'
    actor: str
    target: Optional[str]
    side: str  # 'team' or 'opponent'


class RoundData(TypedDict):
    round_number: int
    events: List[EventData]
    outcome: str  # 'win' or 'loss'
    side: str  # 'Attack' or 'Defense'
    team_economy: str
    opponent_economy: str
    first_blood: str  # 'team' or 'opponent'
    true_first_blood: bool
    first_blood_player: str
    first_death_player: str
    site: Optional[str]  # 'A', 'B', 'C', or None
    plant: bool
    defuse: bool
    awp_info: str  # 'none', 'team', 'opponent', 'both'
    kills_team: int
    kills_opponent: int


class MatchData(TypedDict):
    id: str
    map_name: str
    date: str
    players_agents: Dict[str, str]
    final_score: str
    rounds: List[RoundData]
    total_rounds: int