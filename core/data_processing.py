from difflib import get_close_matches
import numpy as np
import cv2 as cv
from typing import List, Dict, Tuple, Optional, Any, cast
from datetime import datetime
from core.config import load_config
from core.api import get_valid_maps, get_valid_agents
from core.types import (
    RoundData,
    MatchData,
    PlayerData,
    EventData,
    Position,
    ImageRegion,
)
from core.constants import (
    list_of_agents,
    SUMMARY_SIDES_REGION,
    SUMMARY_SCORE_REGION,
    SUMMARY_MAP_REGION,
    TIMELINE_OUTCOME_REGION,
    TIMELINE_ECONOMY_REGION,
    TIMELINE_AWP_REGION,
    EVENT_START_Y,
    EVENT_CHECK_X,
    EVENT_KILL_X,
    EVENT_DEATH_X,
    EVENT_ROW_HEIGHT,
    EVENT_TIMESTAMP_X,
    EVENT_TYPE_X,
    EVENT_ICON_SIZE,
    FIRST_BLOOD_CHECK_Y,
    FIRST_BLOOD_CHECK_X,
    PLAYER_TEAM_START_Y,
    PLAYER_OPPONENT_START_Y,
    PLAYER_CHECK_X,
    PLAYER_NAME_OFFSET,
    PLAYER_REGION_WIDTH,
    PLAYER_ROW_HEIGHT,
    PLAYER_ROW_SPACING,
    PLAYER_TEAM_GREEN_THRESHOLD,
    PLAYER_OPPONENT_RED_THRESHOLD,
)
from core.ocr import extract_text
from core.image_processing import (
    crop_image,
    detect_color,
    get_team_color_from_pixel,
    detect_plant_site,
    extract_agent_sprites,
)
from core.logger import logger


def normalize_agent_name(agent_name: str, valid_agents=None, config=None) -> str:
    """Correct agent name by finding the closest match"""
    logger.push_context(operation="normalize_agent_name", raw_input=agent_name)

    try:
        if valid_agents is None:
            if config is None:
                from core.config import load_config

                config = load_config()
            valid_agents = get_valid_agents(config)

        # Handle the special case for KAY/O which might be entered as KAYO
        if agent_name.upper() in ["KAYO", "KAY/O", "KAY O"]:
            logger.info(f"Normalized agent name from '{agent_name}' to 'KAY/O'")
            return "KAY/O"

        agent_name_lower = agent_name.lower()
        agent_options_lower = [a.lower() for a in valid_agents]

        closest_matches = get_close_matches(
            agent_name_lower, agent_options_lower, n=1, cutoff=0.6
        )

        if closest_matches:
            match_idx = agent_options_lower.index(closest_matches[0])
            normalized = valid_agents[match_idx]

            from difflib import SequenceMatcher

            similarity = SequenceMatcher(
                None, agent_name_lower, closest_matches[0]
            ).ratio()
            logger.debug(
                f"Agent match: '{agent_name}' -> '{normalized}' (similarity: {similarity:.2f})"
            )

            if normalized.lower() != agent_name.lower():
                logger.info(
                    f"Normalized agent name from '{agent_name}' to '{normalized}'"
                )
            return normalized
        else:
            # Ask for manual input as fallback
            logger.warning(f"Could not recognize agent '{agent_name}'")
            logger.user_output(
                f"Could not recognize agent '{agent_name}'. Please enter correct name: "
            )
            corrected = input(
                f"Could not recognize agent '{agent_name}'. Please enter correct name: "
            )

            if corrected.lower() == "kayo":
                return "KAY/O"

            corrected_lower = corrected.lower()
            if corrected_lower in agent_options_lower:
                match_idx = agent_options_lower.index(corrected_lower)
                return valid_agents[match_idx]

            return corrected
    finally:
        logger.clear_context()


def normalize_timestamp(timestamp_str: str) -> int:
    """
    Convert a timestamp string to a normalized integer value in seconds

    Handles formats:
    - "0:XX" (under 60 seconds)
    - "1:XX" (60+ seconds)
    - Special cases like "N/A" (returns 0)

    Args:
        timestamp_str: String timestamp from OCR (e.g., "0:45", "1:20")

    Returns:
        Integer timestamp in seconds
    """
    logger.push_context(operation="normalize_timestamp", raw_timestamp=timestamp_str)

    try:
        if not timestamp_str or not isinstance(timestamp_str, str):
            logger.debug("Empty or non-string timestamp, returning 0")
            return 0

        # Handle special cases
        if timestamp_str.startswith("N"):
            logger.debug("Special timestamp format (N/A), returning 0")
            return 0

        cleaned = (
            timestamp_str.replace(".", "")
            .replace(":", "")
            .replace("T", "")
            .replace("l", "")
        )

        # Handle 0:XX format (under 60 seconds)
        if timestamp_str.startswith("0"):
            cleaned = cleaned.replace("0", "", 1)
            result = int(cleaned) if cleaned.isdigit() else 0
            logger.debug(f"Normalized '0:XX' format to {result} seconds")
            return result

        # Handle 1:XX format (60+ seconds)
        elif timestamp_str.startswith("1"):
            cleaned = cleaned.replace("1", "", 1)
            result = int(cleaned) + 60 if cleaned.isdigit() else 60
            logger.debug(f"Normalized '1:XX' format to {result} seconds")
            return result

        logger.debug(f"Using default timestamp conversion for '{timestamp_str}'")
        return int(cleaned) if cleaned.isdigit() else 0

    except Exception as e:
        logger.error(f"Failed to normalize timestamp '{timestamp_str}': {str(e)}")
        return 0
    finally:
        logger.clear_context()


def normalize_map_name(map_name: str, valid_maps=None, config=None) -> str:
    """Correct map name by finding the closest match"""
    logger.push_context(operation="normalize_map_name", raw_input=map_name)

    try:
        if valid_maps is None:
            if config is None:
                from core.config import load_config

                config = load_config()
            valid_maps = get_valid_maps(config)

        map_name_lower = map_name.lower()
        map_options_lower = [m.lower() for m in valid_maps]

        # Try to find closest match
        closest_matches = get_close_matches(
            map_name_lower, map_options_lower, n=1, cutoff=0.6
        )

        if closest_matches:
            match_idx = map_options_lower.index(closest_matches[0])
            normalized = valid_maps[match_idx]

            from difflib import SequenceMatcher

            similarity = SequenceMatcher(
                None, map_name_lower, closest_matches[0]
            ).ratio()
            logger.debug(
                f"Map match: '{map_name}' -> '{normalized}' (similarity: {similarity:.2f})"
            )

            if normalized.lower() != map_name.lower():
                logger.info(f"Normalized map name from '{map_name}' to '{normalized}'")
            return normalized
        else:
            # No close match found, ask for manual input
            logger.warning(f"Could not normalize map name '{map_name}'")
            logger.user_output(
                f"Could not recognize map '{map_name}'. Please enter correct map name: "
            )
            corrected = input(
                f"Could not recognize map '{map_name}'. Please enter correct map name: "
            )

            corrected_lower = corrected.lower()
            if corrected_lower in map_options_lower:
                match_idx = map_options_lower.index(corrected_lower)
                return valid_maps[match_idx]

            return corrected
    finally:
        logger.clear_context()


def extract_player_data(
    image: np.ndarray, config: Dict[str, Any]
) -> Tuple[List[str], List[str]]:
    """Extract player names and agent names from the scoreboard"""
    logger.push_context(operation="extract_player_data")

    player_list = []
    agent_list = []

    valid_agents = get_valid_agents(config)
    logger.info(f"Using agent list with {len(valid_agents)} agents")

    try:
        # Process team players (top section)
        start_y = PLAYER_TEAM_START_Y
        check_x = PLAYER_CHECK_X

        logger.debug(f"Extracting team players starting at y={start_y}, x={check_x}")

        for i in range(5):
            logger.push_context(team="ally", player_index=i + 1)

            try:
                y = start_y
                while (
                    detect_color(
                        image, Position(y, check_x), f"team_player_{i + 1}_check"
                    )[1]
                    < PLAYER_TEAM_GREEN_THRESHOLD
                ):
                    y += 1
                    if y > 700:  # Safety check
                        logger.warning(
                            f"Reached safety limit when searching for team player {i + 1}"
                        )
                        break

                logger.debug(
                    f"Found team player {i + 1} at y={y}, extracting player region"
                )
                player_region = crop_image(
                    image,
                    ImageRegion(
                        y,
                        y + PLAYER_ROW_HEIGHT,
                        check_x + PLAYER_NAME_OFFSET,
                        check_x + PLAYER_REGION_WIDTH,
                    ),
                    f"team_player_{i + 1}_region",
                )

                logger.debug(f"Running OCR on team player {i + 1} region")
                ocr_result = extract_text(
                    player_region,
                    detail=0,
                    width_ths=25,
                    region_name=f"team_player_{i + 1}",
                )

                if len(ocr_result) < 2:
                    logger.warning(
                        f"OCR failed to detect both player and agent for team player {i + 1}"
                    )

                    if len(ocr_result) == 1:
                        player_name = ocr_result[0]
                        logger.info(
                            f"Detected only player name '{player_name}' for team player {i + 1}, prompting for agent"
                        )
                        logger.user_output(
                            f"Please confirm the agent {player_name} is playing: "
                        )
                        agent_name = input(
                            f"Please confirm the agent {player_name} is playing: "
                        ).title()
                    else:
                        logger.info(
                            f"Failed to detect name and agent for team player {i + 1}, prompting for both"
                        )
                        logger.user_output(
                            f"Please enter player name for position {i + 1}: "
                        )
                        player_name = input(
                            f"Please enter player name for position {i + 1}: "
                        )
                        logger.user_output(f"Please enter agent for {player_name}: ")
                        agent_name = input(
                            f"Please enter agent for {player_name}: "
                        ).title()
                else:
                    player_name, agent_name = ocr_result[0], ocr_result[1]
                    logger.info(
                        f"Successfully detected team player {i + 1}: '{player_name}' playing '{agent_name}'"
                    )

                if agent_name not in valid_agents:
                    logger.debug(
                        f"Agent name '{agent_name}' not in recognized list, normalizing"
                    )
                    original_name = agent_name
                    agent_name = normalize_agent_name(agent_name, valid_agents, config)
                    logger.info(
                        f"Normalized agent name from '{original_name}' to '{agent_name}'"
                    )

                player_list.append(player_name)
                agent_list.append(agent_name)
                start_y = y + PLAYER_ROW_SPACING

            except Exception as e:
                logger.error(f"Error processing team player {i + 1}: {str(e)}")
                player_list.append(f"TeamPlayer{i + 1}")
                agent_list.append("Unknown")
            finally:
                logger.clear_context()  # Clear the player-specific context

        # Process opponent players (bottom section)
        start_y = PLAYER_OPPONENT_START_Y
        logger.debug(f"Extracting opponent players starting at y={start_y}")

        for i in range(5):
            logger.push_context(team="opponent", player_index=i + 1)

            try:
                y = start_y
                while (
                    detect_color(
                        image, Position(y, check_x), f"opponent_player_{i + 1}_check"
                    )[2]
                    < PLAYER_OPPONENT_RED_THRESHOLD
                ):
                    y += 1
                    if y > 900:  # Safety check
                        logger.warning(
                            f"Reached safety limit when searching for opponent player {i + 1}"
                        )
                        break

                logger.debug(
                    f"Found opponent player {i + 1} at y={y}, extracting player region"
                )
                player_region = crop_image(
                    image,
                    ImageRegion(
                        y,
                        y + PLAYER_ROW_HEIGHT,
                        check_x + PLAYER_NAME_OFFSET,
                        check_x + PLAYER_REGION_WIDTH,
                    ),
                    f"opponent_player_{i + 1}_region",
                )

                logger.debug(f"Running OCR on opponent player {i + 1} region")
                ocr_result = extract_text(
                    player_region,
                    detail=0,
                    width_ths=25,
                    region_name=f"opponent_player_{i + 1}",
                )

                if len(ocr_result) < 2:
                    logger.warning(
                        f"OCR failed to detect both player and agent for opponent player {i + 1}"
                    )

                    if len(ocr_result) == 1:
                        player_name = ocr_result[0]
                        logger.info(
                            f"Detected only player name '{player_name}' for opponent player {i + 1}, prompting for agent"
                        )
                        logger.user_output(
                            f"Please confirm the agent {player_name} is playing: "
                        )
                        agent_name = input(
                            f"Please confirm the agent {player_name} is playing: "
                        ).title()
                    else:
                        logger.info(
                            f"Failed to detect name and agent for opponent player {i + 1}, prompting for both"
                        )
                        logger.user_output(
                            f"Please enter opponent player name for position {i + 1}: "
                        )
                        player_name = input(
                            f"Please enter opponent player name for position {i + 1}: "
                        )
                        logger.user_output(f"Please enter agent for {player_name}: ")
                        agent_name = input(
                            f"Please enter agent for {player_name}: "
                        ).title()
                else:
                    player_name, agent_name = ocr_result[0], ocr_result[1]
                    logger.info(
                        f"Successfully detected opponent player {i + 1}: '{player_name}' playing '{agent_name}'"
                    )

                if agent_name not in valid_agents:
                    logger.debug(
                        f"Agent name '{agent_name}' not in recognized list, normalizing"
                    )
                    original_name = agent_name
                    agent_name = normalize_agent_name(agent_name, valid_agents, config)
                    logger.info(
                        f"Normalized agent name from '{original_name}' to '{agent_name}'"
                    )

                player_list.append(player_name)
                agent_list.append(agent_name)
                start_y = y + PLAYER_ROW_SPACING

            except Exception as e:
                logger.error(f"Error processing opponent player {i + 1}: {str(e)}")
                player_list.append(f"OpponentPlayer{i + 1}")
                agent_list.append("Unknown")
            finally:
                logger.clear_context()  # Clear the player-specific context

        logger.info(f"Extracted data for {len(player_list)} players in total")

    except Exception as e:
        logger.error(f"Failed to extract player data: {str(e)}")
        if len(player_list) == 0:
            player_list = [f"Player{i}" for i in range(1, 11)]
            agent_list = ["Unknown" for _ in range(10)]
    finally:
        logger.clear_context()

    return player_list, agent_list


def extract_match_metadata(image: np.ndarray, config: Dict[str, Any]) -> Dict[str, Any]:
    """Extract map name, scores, and other metadata from summary screen"""
    logger.push_context(operation="extract_match_metadata")

    try:
        sides_region = crop_image(image, SUMMARY_SIDES_REGION, "sides_region")
        sides_text = extract_text(sides_region, detail=0, region_name="sides_text")[
            0
        ].lower()

        if "def" in sides_text:
            first_half = "Defense"
            second_half = "Attack"
        else:
            first_half = "Attack"
            second_half = "Defense"

        sides = [first_half] * 12 + [second_half] * 12

        score_region = crop_image(image, SUMMARY_SCORE_REGION, "score_region")
        score_parts = extract_text(score_region, detail=0, region_name="score_text")

        if len(score_parts) >= 3:
            team_score, result, opponent_score = score_parts[0:3]
            logger.debug(
                f"Extracted scores: {team_score}-{opponent_score}, result: {result}"
            )

            # Validate OCR actually read numbers, not garbled text like 'Iq' instead of '13'
            if not team_score.isdigit() or not opponent_score.isdigit():
                logger.warning(
                    f"OCR misread scores: '{team_score}' / '{opponent_score}', prompting for manual input"
                )
                logger.user_output(
                    f"Score OCR failed (read '{team_score}' - '{opponent_score}'). Please correct:"
                )
                logger.user_output("Please enter your team's score: ")
                team_score = input("Please enter your team's score: ")
                logger.user_output("Please enter opponent's score: ")
                opponent_score = input("Please enter opponent's score: ")
                result = "WIN" if int(team_score) > int(opponent_score) else "LOSS"
        else:
            logger.warning("Score extraction failed, prompting for manual input")
            logger.user_output("Please enter your team's score: ")
            team_score = input("Please enter your team's score: ")
            logger.user_output("Please enter opponent's score: ")
            opponent_score = input("Please enter opponent's score: ")
            result = "WIN" if int(team_score) > int(opponent_score) else "LOSS"

        map_region = crop_image(image, SUMMARY_MAP_REGION, "map_region")
        map_text = extract_text(map_region, detail=0, region_name="map_text")

        if map_text:
            raw_map_name = map_text[0]
            logger.debug(f"Raw map name from OCR: '{raw_map_name}'")
        else:
            logger.warning("Map name extraction failed, prompting for manual input")
            logger.user_output("Please enter map name: ")
            raw_map_name = input("Please enter map name: ")

        valid_maps = get_valid_maps(config)
        map_name = normalize_map_name(raw_map_name, valid_maps, config)
        logger.info(f"Using map: {map_name}")

        return {
            "map_name": map_name,
            "team_score": team_score,
            "opponent_score": opponent_score,
            "result": result,
            "sides": sides,
            "total_rounds": int(team_score) + int(opponent_score),
            "final_score": f"{team_score} - {opponent_score}",
            "date": datetime.now().strftime("%d/%m/%Y"),
        }
    finally:
        logger.clear_context()


def extract_round_events(
    timeline_image: np.ndarray, agent_sprites: List[np.ndarray], agent_list: List[str]
) -> List[Tuple[str, str, int, str, str]]:
    """
    Extract kill, plant, and defuse events from a round timeline image

    This function analyzes the pixel colors and visual patterns in a timeline image
    to identify game events and their details (who, what, when).

    Args:
        timeline_image: Screenshot of the round timeline UI
        agent_sprites: Reference images of agent icons for pattern matching
        agent_list: List of agent names corresponding to the sprites

    Returns:
        List of event tuples: (killer_agent, victim_agent, timestamp, event_type, side)
                               where side indicates whether this was a team or opponent event
    """
    logger.push_context(operation="extract_round_events")

    try:
        events = []
        start_y = EVENT_START_Y
        check_x = EVENT_CHECK_X
        kill_x = EVENT_KILL_X
        death_x = EVENT_DEATH_X

        # Scan the timeline from top to bottom looking for events
        current_y = start_y
        while current_y < 1060:  # Stop at bottom of timeline area
            # Events appear as colored pixels; no event = dark/black
            b, g, r = detect_color(timeline_image, Position(current_y, check_x))

            # Skip empty rows (dark pixels indicate no event)
            if g < 100 and r < 100 and b < 100:
                current_y += 1
                continue

            # Green pixels (g > 100) indicate team events, red pixels indicate opponent events
            side = "team" if g > 100 else "opponent"
            logger.debug(f"Found event at y={current_y}, side={side}")

            # Extract timestamp text, located to the left of the event
            timestamp_region = crop_image(
                timeline_image,
                ImageRegion(
                    current_y,
                    current_y + EVENT_ROW_HEIGHT,
                    EVENT_TIMESTAMP_X[0],
                    EVENT_TIMESTAMP_X[1],
                ),
                "timestamp_region",
            )
            timestamp_text = extract_text(
                timestamp_region, detail=0, region_name="timestamp"
            )

            # Skip events where we can't read the timestamp
            if not timestamp_text:
                logger.warning(
                    f"Failed to extract timestamp at y={current_y}, skipping event"
                )
                current_y += EVENT_ROW_HEIGHT
                continue

            # Convert OCR timestamp to seconds using normalized format
            ts_text = timestamp_text[0]
            timestamp = normalize_timestamp(ts_text)

            # Skip events with invalid timestamps
            if timestamp == 0:
                logger.warning(
                    f"Invalid timestamp '{ts_text}' at y={current_y}, skipping event"
                )
                current_y += EVENT_ROW_HEIGHT
                continue

            # Examine text on right side to distinguish plant/defuse from kills
            event_type_region = crop_image(
                timeline_image,
                ImageRegion(
                    current_y,
                    current_y + EVENT_ROW_HEIGHT,
                    EVENT_TYPE_X[0],
                    EVENT_TYPE_X[1],
                ),
                "event_type_region",
            )
            event_type_text = extract_text(
                event_type_region, detail=0, region_name="event_type"
            )

            # Extract the agent icons that appear in the event
            # Killer icon is on the left, victim on the right for kill events
            killer_icon = crop_image(
                timeline_image,
                ImageRegion(
                    current_y,
                    current_y + EVENT_ICON_SIZE,
                    kill_x,
                    kill_x + EVENT_ICON_SIZE,
                ),
                "killer_icon",
            )
            victim_icon = crop_image(
                timeline_image,
                ImageRegion(
                    current_y,
                    current_y + EVENT_ICON_SIZE,
                    death_x,
                    death_x + EVENT_ICON_SIZE,
                ),
                "victim_icon",
            )

            # Identify agents by comparing extracted icons against reference sprites
            # using template matching (higher score = better match)
            killer_scores = []
            victim_scores = []

            for agent_sprite in agent_sprites:
                killer_result = cv.matchTemplate(
                    killer_icon, agent_sprite, cv.TM_CCOEFF_NORMED
                )
                _, killer_max_val, _, _ = cv.minMaxLoc(killer_result)
                killer_scores.append(killer_max_val)

                victim_result = cv.matchTemplate(
                    victim_icon, agent_sprite, cv.TM_CCOEFF_NORMED
                )
                _, victim_max_val, _, _ = cv.minMaxLoc(victim_result)
                victim_scores.append(victim_max_val)

            killer_idx = killer_scores.index(max(killer_scores))
            victim_idx = victim_scores.index(max(victim_scores))

            killer_agent = (
                agent_list[killer_idx] if killer_idx < len(agent_list) else "Unknown"
            )
            victim_agent = (
                agent_list[victim_idx] if victim_idx < len(agent_list) else "Unknown"
            )

            if event_type_text and any("Plant" in t for t in event_type_text):
                event_type = "plant"
            elif event_type_text and any("Defuse" in t for t in event_type_text):
                event_type = "defuse"
            else:
                event_type = "kill"

            logger.info(
                f"Extracted {event_type} ({side}): {killer_agent} → {victim_agent} at {timestamp}s"
            )
            events.append((killer_agent, victim_agent, timestamp, event_type, side))

            current_y += EVENT_ROW_HEIGHT

        return events

    except Exception as e:
        logger.error(f"Failed to extract round events: {str(e)}")
        return []
    finally:
        logger.clear_context()


def extract_first_bloods(timeline_images: List[np.ndarray]) -> List[str]:
    """Determine which team got first blood in each round"""
    first_bloods = []

    for i, image in enumerate(timeline_images):
        logger.push_context(
            operation="process_match_data", sub_operation="first_bloods", round=i
        )
        # Check pixel color at first blood position
        b, g, r = detect_color(
            image, Position(FIRST_BLOOD_CHECK_Y, FIRST_BLOOD_CHECK_X)
        )

        team = "team" if g > 100 else "opponent"
        first_bloods.append(team)

    logger.clear_context()
    return first_bloods


def determine_awp_info(awp_data: List[List[str]]) -> List[str]:
    """Determine AWP (Operator) usage in each round"""
    awp_info = []

    for round_awp in awp_data:
        indices = [i for i, val in enumerate(round_awp) if val == "Operator"]

        if not indices:
            awp_info.append("none")
        elif len(indices) == 1:
            awp_info.append("team" if indices[0] < 11 else "opponent")
        elif len(indices) == 2:
            if all(idx < 11 for idx in indices):
                awp_info.append("team")
            elif all(idx >= 11 for idx in indices):
                awp_info.append("opponent")
            else:
                awp_info.append("both")
        else:
            awp_info.append("both")

    return awp_info


def process_round_outcomes(timeline_images: List[np.ndarray]) -> List[str]:
    """Determine if each round was a win or loss"""
    outcomes = []
    for i, image in enumerate(timeline_images):
        logger.push_context(
            operation="process_match_data", sub_operation="round_outcomes", round=i
        )
        outcome_region = crop_image(image, TIMELINE_OUTCOME_REGION)
        outcome_text = extract_text(outcome_region, detail=0)

        is_loss = any("LOSS" in t.upper() for t in outcome_text)
        outcomes.append("loss" if is_loss else "win")

        logger.debug(f"Round determined {outcomes[i]}")

    logger.clear_context()
    return outcomes


def create_match_data(
    timeline_images: List[np.ndarray],
    scoreboard_image: np.ndarray,
    summary_image: np.ndarray,
    config: Dict[str, Any],
) -> MatchData:
    """Create a complete match data structure from screenshots"""
    logger.push_context(operation="create_match_data")

    try:
        valid_agents = get_valid_agents(config)
        valid_maps = get_valid_maps(config)
        logger.info(
            f"Using {len(valid_agents)} agents and {len(valid_maps)} maps for match data processing"
        )

        metadata = extract_match_metadata(summary_image, config)

        player_list, agent_list = extract_player_data(timeline_images[0], config)
        players_agents = dict(zip(player_list, agent_list))

        agent_sprites = extract_agent_sprites(timeline_images[0])

        outcomes = process_round_outcomes(timeline_images)

        first_bloods = extract_first_bloods(timeline_images)

        round_events = []
        for i, image in enumerate(timeline_images):
            logger.push_context(
                operation="process_match_data", sub_operation="events", round=i + 1
            )
            logger.info(f"Extracting events for round {i + 1}")

            events = extract_round_events(image, agent_sprites, agent_list)
            round_events.append(events)
            logger.clear_context()

        economy_regions = [
            crop_image(img, TIMELINE_ECONOMY_REGION) for img in timeline_images
        ]
        economy_data = [
            extract_text(region, detail=0, region_name="buy_data")
            for region in economy_regions
        ]
        team_economy = [eco[0] if eco else "0" for eco in economy_data]
        opponent_economy = [eco[1] if len(eco) > 1 else "0" for eco in economy_data]

        awp_regions = [crop_image(img, TIMELINE_AWP_REGION) for img in timeline_images]
        awp_data = [extract_text(region, detail=0) for region in awp_regions]
        awp_info = determine_awp_info(awp_data)

        plant_site_list = [
            detect_plant_site(img, metadata["map_name"]) for img in timeline_images
        ]

        round_events = []
        for i, image in enumerate(timeline_images):
            logger.push_context(
                operation="process_match_data", sub_operation="events", round=i
            )
            events = extract_round_events(image, agent_sprites, agent_list)
            round_events.append(events)
            logger.clear_context()

        rounds = []
        for i in range(len(timeline_images)):
            if i >= len(outcomes) or i >= len(first_bloods):
                continue

            logger.push_context(operation="process_round_data", round_number=i + 1)

            try:
                formatted_events, first_blood_player, first_death_player = (
                    format_round_events(round_events[i], player_list, agent_list)
                )

                has_plant = False
                has_defuse = False
                for _, _, _, event_type, _ in round_events[i]:
                    if event_type == "plant":
                        has_plant = True
                    elif event_type == "defuse":
                        has_defuse = True

                # Calculate kills for each team
                team_kills = 0
                opponent_kills = 0
                for killer, victim, _, event_type, _ in round_events[i]:
                    if event_type == "kill":
                        killer_idx = (
                            agent_list.index(killer) if killer in agent_list else -1
                        )
                        if 0 <= killer_idx < 5:  # Team player
                            team_kills += 1
                        elif 5 <= killer_idx < 10:  # Opponent player
                            opponent_kills += 1

                # Adjust for plants/defuses which are also counted as events
                side = metadata["sides"][i] if i < len(metadata["sides"]) else "Unknown"
                if has_plant:
                    if side == "Attack":
                        team_kills -= 1
                    else:
                        opponent_kills -= 1

                if has_defuse:
                    if side == "Defense":
                        team_kills -= 1
                    else:
                        opponent_kills -= 1

                round_data: RoundData = {
                    "round_number": i + 1,
                    "events": formatted_events,
                    "outcome": outcomes[i],
                    "side": side,
                    "team_economy": team_economy[i] if i < len(team_economy) else "0",
                    "opponent_economy": opponent_economy[i]
                    if i < len(opponent_economy)
                    else "0",
                    "first_blood": first_bloods[i]
                    if i < len(first_bloods)
                    else "unknown",
                    "true_first_blood": True,  # Could be enhanced with additional logic
                    "first_blood_player": first_blood_player,
                    "first_death_player": first_death_player,
                    "site": plant_site_list[i]
                    if i < len(plant_site_list) and plant_site_list[i]
                    else None,
                    "plant": has_plant,
                    "defuse": has_defuse,
                    "awp_info": awp_info[i] if i < len(awp_info) else "none",
                    "kills_team": team_kills,
                    "kills_opponent": opponent_kills,
                }

                rounds.append(round_data)
            finally:
                logger.clear_context()

        valid_rounds = []
        logger.push_context(operation="validate_match_data")
        try:
            for round_data in rounds:
                if validate_round_data(round_data):
                    valid_rounds.append(round_data)
                else:
                    logger.warning(
                        f"Round {round_data['round_number']} validation failed, data may be incomplete"
                    )
                    valid_rounds.append(round_data)
        finally:
            logger.clear_context()

        match_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        match_id = f"M_{metadata['map_name']}_{match_time}"

        match_data: MatchData = {
            "id": match_id,
            "map_name": metadata["map_name"],
            "date": metadata["date"],
            "players_agents": players_agents,
            "final_score": metadata["final_score"],
            "rounds": valid_rounds,  # Use validated rounds here
            "total_rounds": metadata["total_rounds"],
        }

        return match_data
    finally:
        logger.clear_context()


def format_round_events(
    round_events: List[Tuple[str, str, int, str, str]],
    player_list: List[str],
    agent_list: List[str],
) -> Tuple[List[EventData], str, str]:
    """
    Format raw event tuples into EventData objects and identify first blood/death players

    Args:
        round_events: List of event tuples (killer_agent, victim_agent, timestamp, event_type, side)
        player_list: List of player names
        agent_list: List of agent names

    Returns:
        Tuple containing (formatted_events, first_blood_player, first_death_player)
    """
    logger.push_context(operation="format_round_events")

    try:
        # Sort events by timestamp for proper ordering
        sorted_events = sorted(round_events, key=lambda x: x[2])

        formatted_events = []
        first_blood_player = ""
        first_death_player = ""

        for event_tuple in sorted_events:
            # Handle both old format (4 elements) and new format (5 elements with side)
            if len(event_tuple) == 5:
                killer_agent, victim_agent, timestamp, event_type, side = event_tuple
            else:
                killer_agent, victim_agent, timestamp, event_type = event_tuple
                killer_idx = (
                    agent_list.index(killer_agent) if killer_agent in agent_list else -1
                )
                side = "team" if 0 <= killer_idx < 5 else "opponent"

            logger.push_context(event_type=event_type, timestamp=timestamp, side=side)

            try:
                if event_type == "kill":
                    event_data, killer_player, victim_player = _format_kill_event(
                        killer_agent,
                        victim_agent,
                        timestamp,
                        player_list,
                        agent_list,
                        side,
                    )
                    formatted_events.append(event_data)

                    # Record first blood/death if not already set
                    if not first_blood_player:
                        first_blood_player = killer_player
                        first_death_player = victim_player
                        logger.debug(
                            f"Recorded first blood: {killer_player} killed {victim_player}"
                        )

                elif event_type in ["plant", "defuse"]:
                    event_data = _format_utility_event(
                        killer_agent,
                        event_type,
                        timestamp,
                        player_list,
                        agent_list,
                        side,
                    )
                    formatted_events.append(event_data)
            finally:
                logger.clear_context()  # Clear event-specific context

        return formatted_events, first_blood_player, first_death_player
    finally:
        logger.clear_context()  # Clear operation context


def _format_kill_event(
    killer_agent: str,
    victim_agent: str,
    timestamp: int,
    player_list: List[str],
    agent_list: List[str],
    side: str,
) -> Tuple[EventData, str, str]:
    """
    Format a kill event into an EventData object, handling duplicate agents correctly

    Args:
        killer_agent: The agent name of the killer
        victim_agent: The agent name of the victim
        timestamp: Event timestamp
        player_list: List of player names
        agent_list: List of agent names
        side: The side of the killer ('team' or 'opponent')

    Returns:
        Tuple containing (event_data, killer_player_name, victim_player_name)
    """
    # Find all indices where this agent appears
    killer_indices = [i for i, agent in enumerate(agent_list) if agent == killer_agent]
    victim_indices = [i for i, agent in enumerate(agent_list) if agent == victim_agent]

    # Team side = indices 0-4, Opponent side = indices 5-9
    if side == "team":
        team_killer_indices = [idx for idx in killer_indices if 0 <= idx < 5]
        if team_killer_indices:
            killer_idx = team_killer_indices[0]
        else:
            killer_idx = killer_indices[0] if killer_indices else -1
    else:
        opponent_killer_indices = [idx for idx in killer_indices if 5 <= idx < 10]
        if opponent_killer_indices:
            killer_idx = opponent_killer_indices[0]
        else:
            killer_idx = killer_indices[0] if killer_indices else -1

    if 0 <= killer_idx < 5:
        opponent_victim_indices = [idx for idx in victim_indices if 5 <= idx < 10]
        if opponent_victim_indices:
            victim_idx = opponent_victim_indices[0]
        else:
            victim_idx = victim_indices[0] if victim_indices else -1
    else:
        team_victim_indices = [idx for idx in victim_indices if 0 <= idx < 5]
        if team_victim_indices:
            victim_idx = team_victim_indices[0]
        else:
            victim_idx = victim_indices[0] if victim_indices else -1

    killer_player = (
        player_list[killer_idx] if 0 <= killer_idx < len(player_list) else killer_agent
    )
    victim_player = (
        player_list[victim_idx] if 0 <= victim_idx < len(player_list) else victim_agent
    )

    event_data: EventData = {
        "timestamp": timestamp,
        "event_type": "kill",
        "actor": killer_player,
        "target": victim_player,
        "side": side,
    }

    return event_data, killer_player, victim_player


def _format_utility_event(
    actor_agent: str,
    event_type: str,
    timestamp: int,
    player_list: List[str],
    agent_list: List[str],
    side: str,
) -> EventData:
    """
    Format a utility event (plant/defuse) into an EventData object

    Args:
        actor_agent: The agent name of the actor
        event_type: The type of event ('plant' or 'defuse')
        timestamp: Event timestamp
        player_list: List of player names
        agent_list: List of agent names
        side: The side of the actor ('team' or 'opponent')

    Returns:
        EventData object
    """
    # Find all indices of actor_agent in agent_list
    actor_indices = [i for i, agent in enumerate(agent_list) if agent == actor_agent]

    if side == "team":
        team_actor_indices = [idx for idx in actor_indices if 0 <= idx < 5]
        if team_actor_indices:
            actor_idx = team_actor_indices[0]
        else:
            actor_idx = actor_indices[0] if actor_indices else -1
    else:
        opponent_actor_indices = [idx for idx in actor_indices if 5 <= idx < 10]
        if opponent_actor_indices:
            actor_idx = opponent_actor_indices[0]
        else:
            actor_idx = actor_indices[0] if actor_indices else -1

    actor_player = (
        player_list[actor_idx] if 0 <= actor_idx < len(player_list) else actor_agent
    )

    event_data: EventData = {
        "timestamp": timestamp,
        "event_type": event_type,
        "actor": actor_player,
        "target": None,  # No target for plant/defuse
        "side": side,
    }

    return event_data


def validate_round_data(round_data: RoundData) -> bool:
    """
    Validate that a round data object has all required fields properly populated

    Args:
        round_data: The RoundData object to validate

    Returns:
        True if data is valid, False otherwise
    """
    logger.push_context(
        operation="validate_round_data", round_number=round_data["round_number"]
    )

    try:
        is_valid = True

        if (
            round_data["kills_team"] + round_data["kills_opponent"] > 0
        ) and not round_data["events"]:
            logger.warning(
                f"Round has {round_data['kills_team'] + round_data['kills_opponent']} kills but no events"
            )
            is_valid = False

        if (
            round_data["first_blood"] != "unknown"
            and not round_data["first_blood_player"]
        ):
            logger.warning(
                f"Round has first blood team ({round_data['first_blood']}) but no player assigned"
            )
            is_valid = False

        if round_data["plant"] and not any(
            e["event_type"] == "plant" for e in round_data["events"]
        ):
            logger.warning(f"Round has plant=True but no plant event")
            is_valid = False

        if round_data["defuse"] and not any(
            e["event_type"] == "defuse" for e in round_data["events"]
        ):
            logger.warning(f"Round has defuse=True but no defuse event")
            is_valid = False

        return is_valid
    finally:
        logger.clear_context()
