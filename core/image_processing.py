import cv2 as cv
import numpy as np
import os
from typing import Tuple, List, Dict, Optional, Any
from core.types import ImageRegion, Position
from core.ocr import extract_text
from core.constants import list_of_agents


def crop_image(image: np.ndarray, region: ImageRegion) -> np.ndarray:
    """Crop image to specified region"""
    return image[region.y_start:region.y_end, region.x_start:region.x_end]


def detect_color(image: np.ndarray, position: Position) -> Tuple[int, int, int]:
    """Get BGR color at specific pixel"""
    return image[position.y, position.x]


def find_template(image: np.ndarray, template: np.ndarray) -> Tuple[float, Tuple[int, int]]:
    """Find template in image and return match confidence and position"""
    result = cv.matchTemplate(image, template, cv.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
    return max_val, max_loc


def enhance_for_ocr(image: np.ndarray) -> np.ndarray:
    """Enhance image for better OCR results"""
    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    enhanced = cv.convertScaleAbs(gray, alpha=1.5, beta=0)
    return enhanced


def get_team_color_from_pixel(image: np.ndarray, position: Position) -> str:
    """Determine if a pixel belongs to team or opponent based on color"""
    b, g, r = detect_color(image, position)

    # Team colors are typically green-ish (g > 100)
    # Opponent colors are typically red-ish (r > 100, g < 100)
    if g > 100:
        return 'team'
    elif r > 100 and g < 100:
        return 'opponent'
    else:
        return 'unknown'


def detect_plant_site(image: np.ndarray, map_name: str) -> Optional[str]:
    """Detect planted spike location on the minimap"""
    spike_path = os.path.join(os.getcwd(), "spike.png")

    if not os.path.exists(spike_path):
        return None

    spike = cv.imread(spike_path)
    minimap = crop_image(image, ImageRegion(490, 990, 1270, 1770))

    max_val, max_loc = find_template(minimap, spike)
    x, y = max_loc

    if max_val <= 0.70:
        return None

    # Logic for determining site based on map and location
    if map_name == 'bind':
        return 'B' if x < 250 else 'A'
    elif map_name == 'ascent':
        return 'B' if y < 250 else 'A'
    elif map_name == 'haven':
        if y < 150:
            return 'A'
        elif 150 < y < 280:
            return 'B'
        else:
            return 'C'
    elif map_name == 'lotus':
        if x < 150:
            return 'C'
        elif 150 < x < 300:
            return 'B'
        else:
            return 'A'
    elif map_name == 'pearl':
        if x < 250 and 90 < y < 210:
            return 'B'
        if x > 250 and 90 < y < 210:
            return 'A'
    elif map_name == 'fracture':
        if x > 250 and 190 < y < 290:
            return 'A'
        if x < 250 and 190 < y < 290:
            return 'B'
    elif map_name == 'split':
        return 'B' if y > 250 else 'A'
    elif map_name == 'sunset':
        return 'A' if x > 250 else 'B'
    elif map_name == 'breeze':
        return 'A' if x > 250 else 'B'
    elif map_name == 'icebox':
        return 'A' if y > 200 else 'B'

    return 'unclear'


def extract_agent_sprites(image: np.ndarray) -> List[np.ndarray]:
    """Extract agent icon sprites from the scoreboard"""
    agent_sprites = []

    # Team agents (top half)
    start_y = 503
    check_x = 161

    for i in range(5):
        y = start_y
        while detect_color(image, Position(y, check_x))[1] < 100:  # green < 100
            y += 1
            if y > 700:  # Safety check
                break

        icon_x = check_x + 3
        agent_sprite = crop_image(image, ImageRegion(y, y + 40, icon_x, icon_x + 40))
        agent_sprites.append(agent_sprite)
        start_y = y + 42

    # Opponent agents (bottom half)
    start_y = 724

    for i in range(5):
        y = start_y
        while detect_color(image, Position(y, check_x))[2] < 80:  # red < 80
            y += 1
            if y > 900:  # Safety check
                break

        icon_x = check_x + 3
        agent_sprite = crop_image(image, ImageRegion(y, y + 40, icon_x, icon_x + 40))
        agent_sprites.append(agent_sprite)
        start_y = y + 42

    return agent_sprites