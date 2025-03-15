import cv2 as cv
import numpy as np
import os
from typing import Tuple, List, Dict, Optional, Any
from core.types import ImageRegion, Position
from core.ocr import extract_text
from core.constants import list_of_agents
from core.logger import logger


def crop_image(image: np.ndarray, region: ImageRegion, description: str = "unnamed") -> np.ndarray:
    """
    Crop image to specified region

    Args:
        image: The image to crop
        region: The region coordinates
        description: A descriptive name for the region (for better logging)
    """
    logger.debug(
        f"Cropping '{description}' region: y={region.y_start}:{region.y_end}, x={region.x_start}:{region.x_end}")

    if (region.y_start < 0 or region.y_end > image.shape[0] or
            region.x_start < 0 or region.x_end > image.shape[1]):
        logger.warning(f"Cropping region for '{description}' is out of bounds: "
                       f"image shape={image.shape}, region={region}")

    try:
        cropped = image[region.y_start:region.y_end, region.x_start:region.x_end]
        logger.debug(f"Cropped '{description}' region to shape {cropped.shape}")
        return cropped
    except Exception as e:
        logger.error(f"Failed to crop '{description}' region: {str(e)}")
        # Return a small empty image in case of error
        return np.zeros((10, 10, 3), dtype=np.uint8)


def detect_color(image: np.ndarray, position: Position, description: str = "pixel") -> Tuple[int, int, int]:
    """
    Get BGR color at specific pixel

    Args:
        image: The image to get color from
        position: The pixel coordinates
        description: A descriptive name for the pixel (for better logging)
    """
    if position.y < 0 or position.y >= image.shape[0] or position.x < 0 or position.x >= image.shape[1]:
        logger.warning(f"Position for '{description}' is out of bounds: "
                       f"image shape={image.shape}, position={position}")
        return (0, 0, 0)

    try:
        color = image[position.y, position.x]
        logger.debug(f"Detected color at '{description}' ({position}): BGR={color}")
        return color
    except Exception as e:
        logger.error(f"Failed to detect color at '{description}' ({position}): {str(e)}")
        return (0, 0, 0)


def find_template(image: np.ndarray, template: np.ndarray, template_name: str = "unnamed") -> Tuple[
    float, Tuple[int, int]]:
    """
    Find template in image and return match confidence and position

    Args:
        image: The image to search in
        template: The template to search for
        template_name: A descriptive name for the template (for better logging)
    """
    logger.debug(f"Finding template '{template_name}' (shape: {template.shape}) in image (shape: {image.shape})")

    try:
        result = cv.matchTemplate(image, template, cv.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
        logger.debug(f"Template match for '{template_name}': confidence={max_val:.4f}, position={max_loc}")
        return max_val, max_loc
    except Exception as e:
        logger.error(f"Template matching failed for '{template_name}': {str(e)}")
        return 0.0, (0, 0)


def enhance_for_ocr(image: np.ndarray, region_name: str = "unnamed") -> np.ndarray:
    """
    Enhance image for better OCR results

    Args:
        image: The image to enhance
        region_name: A descriptive name for the image region (for better logging)
    """
    logger.debug(f"Enhancing '{region_name}' region for OCR (shape: {image.shape})")

    try:
        gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
        enhanced = cv.convertScaleAbs(gray, alpha=1.5, beta=0)
        logger.debug(f"Enhanced '{region_name}' region: converted to grayscale with alpha=1.5")
        return enhanced
    except Exception as e:
        logger.error(f"Failed to enhance '{region_name}' region for OCR: {str(e)}")
        return image  # Return original image on error


def get_team_color_from_pixel(image: np.ndarray, position: Position, description: str = "team pixel") -> str:
    """
    Determine if a pixel belongs to team or opponent based on color

    Args:
        image: The image to check
        position: The pixel coordinates
        description: A descriptive name for the pixel (for better logging)
    """
    try:
        b, g, r = detect_color(image, position, description)

        # Team colors are typically green-ish (g > 100)
        # Opponent colors are typically red-ish (r > 100, g < 100)
        if g > 100:
            logger.debug(f"Detected team color at '{description}' ({position}): BGR=({b},{g},{r})")
            return 'team'
        elif r > 100 and g < 100:
            logger.debug(f"Detected opponent color at '{description}' ({position}): BGR=({b},{g},{r})")
            return 'opponent'
        else:
            logger.warning(
                f"Ambiguous color at '{description}' ({position}): BGR=({b},{g},{r}) - cannot determine team")
            return 'unknown'
    except Exception as e:
        logger.error(f"Failed to determine team color at '{description}' ({position}): {str(e)}")
        return 'unknown'


def detect_plant_site(image: np.ndarray, map_name: str) -> Optional[str]:
    """
    Detect planted spike location on the minimap

    Args:
        image: The image containing the minimap
        map_name: The name of the map being played
    """
    logger.push_context(operation="detect_plant_site", map=map_name)

    try:
        spike_path = os.path.join(os.getcwd(), "spike.png")

        if not os.path.exists(spike_path):
            logger.warning(f"Spike template image not found at {spike_path}")
            logger.clear_context()
            return None

        logger.debug(f"Loading spike template from {spike_path}")
        spike = cv.imread(spike_path)
        if spike is None:
            logger.warning("Failed to load spike template image")
            logger.clear_context()
            return None

        logger.debug("Cropping minimap region")
        minimap = crop_image(image, ImageRegion(490, 990, 1270, 1770), "minimap")

        logger.debug("Searching for spike on minimap")
        max_val, max_loc = find_template(minimap, spike, "spike")
        x, y = max_loc

        if max_val <= 0.70:
            logger.info(f"Spike not detected on minimap (confidence: {max_val:.2f})")
            logger.clear_context()
            return None

        logger.debug(f"Spike detected at position ({x}, {y}) with confidence {max_val:.2f}")

        # Logic for determining site based on map and location
        site = None
        if map_name == 'bind':
            site = 'B' if x < 250 else 'A'
        elif map_name == 'ascent':
            site = 'B' if y < 250 else 'A'
        elif map_name == 'haven':
            if y < 150:
                site = 'A'
            elif 150 < y < 280:
                site = 'B'
            else:
                site = 'C'
        elif map_name == 'lotus':
            if x < 150:
                site = 'C'
            elif 150 < x < 300:
                site = 'B'
            else:
                site = 'A'
        elif map_name == 'pearl':
            if x < 250 and 90 < y < 210:
                site = 'B'
            if x > 250 and 90 < y < 210:
                site = 'A'
        elif map_name == 'fracture':
            if x > 250 and 190 < y < 290:
                site = 'A'
            if x < 250 and 190 < y < 290:
                site = 'B'
        elif map_name == 'split':
            site = 'B' if y > 250 else 'A'
        elif map_name == 'sunset':
            site = 'A' if x > 250 else 'B'
        elif map_name == 'breeze':
            site = 'A' if x > 250 else 'B'
        elif map_name == 'icebox':
            site = 'A' if y > 200 else 'B'
        else:
            site = 'unclear'

        logger.info(f"Detected spike planted at site {site} on {map_name}")
        return site

    except Exception as e:
        logger.error(f"Failed to detect plant site: {str(e)}")
        return None
    finally:
        logger.clear_context()


def extract_agent_sprites(image: np.ndarray) -> List[np.ndarray]:
    """
    Extract agent icon sprites from the scoreboard

    Args:
        image: The scoreboard image
    """
    logger.push_context(operation="extract_agent_sprites")
    agent_sprites = []

    try:
        # Team agents (top half)
        start_y = 503
        check_x = 161

        logger.debug(f"Extracting team agent sprites starting from y={start_y}, x={check_x}")

        for i in range(5):
            y = start_y
            while detect_color(image, Position(y, check_x), f"team_agent_{i + 1}_check")[1] < 100:  # green < 100
                y += 1
                if y > 700:  # Safety check
                    logger.warning(f"Safety limit reached while finding team agent {i + 1}")
                    break

            icon_x = check_x + 3
            logger.debug(f"Found team agent {i + 1} at y={y}, extracting sprite")

            try:
                agent_sprite = crop_image(image, ImageRegion(y, y + 40, icon_x, icon_x + 40),
                                          f"team_agent_{i + 1}_sprite")
                agent_sprites.append(agent_sprite)
                logger.debug(f"Team agent {i + 1} sprite extracted with shape {agent_sprite.shape}")
            except Exception as e:
                logger.error(f"Failed to extract team agent {i + 1} sprite: {str(e)}")
                # Add a blank sprite to maintain indexing
                agent_sprites.append(np.zeros((40, 40, 3), dtype=np.uint8))

            start_y = y + 42

        # Opponent agents (bottom half)
        start_y = 724
        logger.debug(f"Extracting opponent agent sprites starting from y={start_y}")

        for i in range(5):
            y = start_y
            while detect_color(image, Position(y, check_x), f"opponent_agent_{i + 1}_check")[2] < 80:  # red < 80
                y += 1
                if y > 900:  # Safety check
                    logger.warning(f"Safety limit reached while finding opponent agent {i + 1}")
                    break

            icon_x = check_x + 3
            logger.debug(f"Found opponent agent {i + 1} at y={y}, extracting sprite")

            try:
                agent_sprite = crop_image(image, ImageRegion(y, y + 40, icon_x, icon_x + 40),
                                          f"opponent_agent_{i + 1}_sprite")
                agent_sprites.append(agent_sprite)
                logger.debug(f"Opponent agent {i + 1} sprite extracted with shape {agent_sprite.shape}")
            except Exception as e:
                logger.error(f"Failed to extract opponent agent {i + 1} sprite: {str(e)}")
                # Add a blank sprite to maintain indexing
                agent_sprites.append(np.zeros((40, 40, 3), dtype=np.uint8))

            start_y = y + 42

        logger.info(f"Extracted {len(agent_sprites)} agent sprites in total")
        return agent_sprites

    except Exception as e:
        logger.error(f"Failed to extract agent sprites: {str(e)}")
        return []
    finally:
        logger.clear_context()