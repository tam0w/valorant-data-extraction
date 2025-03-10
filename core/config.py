import yaml
import os
from typing import Dict, Any, Optional
from pathlib import Path


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """Load configuration from YAML file"""
    default_config = {
        'output_dir': str(Path.home() / "Documents" / "practistics" / "matches"),
        'log_dir': str(Path.home() / "Documents" / "practistics" / "error_logs"),
        'ocr': {
            'lang': ['en'],
            'download_enabled': True
        }
    }

    if not config_path:
        return default_config

    try:
        with open(config_path, 'r') as f:
            user_config = yaml.safe_load(f)
            if user_config:
                # Merge user config with default
                default_config.update(user_config)
    except Exception as e:
        print(f"Error loading config: {e}")

    # Ensure directories exist
    os.makedirs(default_config['output_dir'], exist_ok=True)
    os.makedirs(default_config['log_dir'], exist_ok=True)

    return default_config


def get_config_value(config: Dict[str, Any], key: str, default: Any = None) -> Any:
    """Get configuration value with dot notation support"""
    keys = key.split('.')
    value = config

    try:
        for k in keys:
            value = value[k]
        return value
    except (KeyError, TypeError):
        return default