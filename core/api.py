# core/api.py
import os
import json
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
import requests
from core.logger import logger
from core.constants import list_of_agents, list_of_maps
from core.config import get_config_value


def _ensure_cache_dir(config: Dict[str, Any]) -> Path:
    """Ensure the cache directory exists and return its path"""
    # Get cache directory from config, with fallback
    cache_dir = Path(get_config_value(config, 'cache_dir',
                                      str(Path.home() / ".practistics" / "cache")))
    os.makedirs(cache_dir, exist_ok=True)
    return cache_dir


def _get_from_cache(config: Dict[str, Any], cache_name: str) -> Optional[List[str]]:
    """Get data from cache if it exists and isn't too old"""
    logger.push_context(operation="get_from_cache", cache_name=cache_name)

    try:
        # Get cache settings from config
        max_age_days = get_config_value(config, f'cache.{cache_name}.max_age_days', 7)
        enabled = get_config_value(config, f'cache.enabled', True)

        if not enabled:
            logger.debug("Cache is disabled in config")
            return None

        cache_dir = _ensure_cache_dir(config)
        cache_file = cache_dir / f"{cache_name}_cache.json"

        if not cache_file.exists():
            logger.debug(f"Cache file does not exist: {cache_file}")
            return None

        modified_time = os.path.getmtime(cache_file)
        cache_age = time.time() - modified_time
        max_age_seconds = max_age_days * 24 * 60 * 60

        if cache_age > max_age_seconds:
            logger.debug(f"Cache is too old: {cache_age / 86400:.1f} days (max: {max_age_days} days)")
            return None

        with open(cache_file, 'r') as f:
            data = json.load(f)
            logger.debug(f"Using cached {cache_name} data: {len(data)} items")
            return data
    except Exception as e:
        logger.warning(f"Error reading {cache_name} cache: {str(e)}")
        return None
    finally:
        logger.clear_context()


def _save_to_cache(config: Dict[str, Any], cache_name: str, data: List[str]) -> bool:
    """Save data to cache file"""
    logger.push_context(operation="save_to_cache", cache_name=cache_name)

    try:
        # Check if cache is enabled
        enabled = get_config_value(config, f'cache.enabled', True)
        if not enabled:
            logger.debug("Cache is disabled in config, skipping save")
            return False

        cache_dir = _ensure_cache_dir(config)
        cache_file = cache_dir / f"{cache_name}_cache.json"

        with open(cache_file, 'w') as f:
            json.dump(data, f)

        logger.debug(f"Saved {len(data)} items to {cache_name} cache")
        return True
    except Exception as e:
        logger.error(f"Error saving to {cache_name} cache: {str(e)}")
        return False
    finally:
        logger.clear_context()


def _fetch_from_api(config: Dict[str, Any], endpoint: str, extract_key: str, filter_func=None) -> Optional[List[str]]:
    """Fetch data from the VALORANT API"""
    logger.push_context(operation="fetch_from_api", endpoint=endpoint)

    try:
        # Get API settings from config
        api_timeout = get_config_value(config, 'api.timeout', 10)
        api_enabled = get_config_value(config, 'api.enabled', True)
        api_base_url = get_config_value(config, 'api.base_url', "https://valorant-api.com/v1")

        if not api_enabled:
            logger.info("API is disabled in config")
            return None

        logger.info(f"Fetching data from VALORANT API: {endpoint}")
        response = requests.get(f"{api_base_url}/{endpoint}", timeout=api_timeout)

        if response.status_code == 200:
            data = response.json()
            items = [item[extract_key] for item in data["data"]]

            if filter_func:
                items = [item for item in items if filter_func(item)]

            logger.info(f"Successfully fetched {len(items)} items from API")
            return items
        else:
            logger.error(f"API request failed with status code {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"Error fetching from API: {str(e)}")
        return None
    finally:
        logger.clear_context()


def fetch_agents_from_api(config: Dict[str, Any]) -> List[str]:
    """Fetch agent list from VALORANT API with caching"""
    logger.push_context(operation="fetch_agents")

    try:
        # Check cache first
        cached_data = _get_from_cache(config, "agents")
        if cached_data:
            return cached_data

        # Fetch from API
        agents = _fetch_from_api(
            config,
            "agents?isPlayableCharacter=true",
            extract_key="displayName"
        )

        if agents:
            _save_to_cache(config, "agents", agents)
            return agents

        # Fallback to hardcoded list
        logger.info("Using hardcoded agent list as fallback")
        return list_of_agents
    except Exception as e:
        logger.error(f"Error fetching agents: {str(e)}")
        return list_of_agents
    finally:
        logger.clear_context()


def fetch_maps_from_api(config: Dict[str, Any]) -> List[str]:
    """Fetch map list from VALORANT API with caching"""
    logger.push_context(operation="fetch_maps")

    try:
        # Check cache first
        cached_data = _get_from_cache(config, "maps")
        if cached_data:
            return cached_data

        # Fetch from API
        # Filter function to remove The Range and other non-standard maps
        def is_standard_map(name: str) -> bool:
            return name != "The Range" and "RANGE" not in name.upper()

        maps = _fetch_from_api(
            config,
            "maps",
            extract_key="displayName",
            filter_func=is_standard_map
        )

        if maps:
            _save_to_cache(config, "maps", maps)
            return maps

        # Fallback to hardcoded list
        logger.info("Using hardcoded map list as fallback")
        return list_of_maps
    except Exception as e:
        logger.error(f"Error fetching maps: {str(e)}")
        return list_of_maps
    finally:
        logger.clear_context()


def get_valid_agents(config: Dict[str, Any], offline_mode: bool = False) -> List[str]:
    """Get the list of valid agents, preferring API data if available"""
    if offline_mode:
        logger.info("Using offline mode with hardcoded agent list")
        return list_of_agents

    try:
        return fetch_agents_from_api(config)
    except Exception as e:
        logger.warning(f"Error getting valid agents: {str(e)}")
        return list_of_agents


def get_valid_maps(config: Dict[str, Any], offline_mode: bool = False) -> List[str]:
    """Get the list of valid maps, preferring API data if available"""
    if offline_mode:
        logger.info("Using offline mode with hardcoded map list")
        return list_of_maps

    try:
        return fetch_maps_from_api(config)
    except Exception as e:
        logger.warning(f"Error getting valid maps: {str(e)}")
        return list_of_maps


def clear_cache(config: Dict[str, Any], cache_name: str = None) -> bool:
    """Clear specified cache or all caches to force a refresh on next fetch"""
    logger.push_context(operation="clear_cache", cache_name=cache_name)

    try:
        cache_dir = _ensure_cache_dir(config)
        success = False

        if cache_name:
            # Clear specific cache
            cache_file = cache_dir / f"{cache_name}_cache.json"
            if cache_file.exists():
                os.remove(cache_file)
                logger.info(f"Cleared {cache_name} cache")
                success = True
        else:
            # Clear all caches
            for cache_file in cache_dir.glob("*_cache.json"):
                os.remove(cache_file)
                logger.info(f"Cleared cache: {cache_file.name}")
                success = True

        return success
    except Exception as e:
        logger.error(f"Error clearing cache: {str(e)}")
        return False
    finally:
        logger.clear_context()


def get_cache_info(config: Dict[str, Any], cache_name: str = None) -> Dict[str, Any]:
    """Get information about the specified cache or all caches"""
    logger.push_context(operation="get_cache_info", cache_name=cache_name)

    try:
        cache_dir = _ensure_cache_dir(config)
        result = {}

        if cache_name:
            # Get info for specific cache
            cache_file = cache_dir / f"{cache_name}_cache.json"
            result[cache_name] = _get_single_cache_info(cache_file, cache_name, config)
        else:
            # Get info for all caches
            for cache_file in cache_dir.glob("*_cache.json"):
                name = cache_file.name.replace("_cache.json", "")
                result[name] = _get_single_cache_info(cache_file, name, config)

        return result
    except Exception as e:
        logger.error(f"Error getting cache info: {str(e)}")
        return {"error": str(e)}
    finally:
        logger.clear_context()


def _get_single_cache_info(cache_file: Path, cache_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """Get information about a single cache file"""
    if not cache_file.exists():
        return {"exists": False}

    try:
        modified_time = os.path.getmtime(cache_file)
        age_seconds = time.time() - modified_time

        # Get max age from config
        max_age_days = get_config_value(config, f'cache.{cache_name}.max_age_days', 7)
        max_age_seconds = max_age_days * 24 * 60 * 60

        with open(cache_file, 'r') as f:
            data = json.load(f)

        return {
            "exists": True,
            "age_seconds": age_seconds,
            "age_days": age_seconds / (24 * 60 * 60),
            "fresh": age_seconds < max_age_seconds,
            "max_age_days": max_age_days,
            "item_count": len(data),
            "items": data,
            "file_size": os.path.getsize(cache_file)
        }
    except Exception as e:
        return {"exists": True, "error": str(e)}