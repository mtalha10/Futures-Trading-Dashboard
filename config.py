# config.py (New configuration management)
import os
import yaml


def load_config(config_path: str = 'config.yaml'):
    """
    Load configuration from a YAML file.

    Args:
        config_path (str): Path to the configuration file

    Returns:
        Dict containing configuration settings
    """
    default_config = {
        'database': {
            'host': 'localhost',
            'port': 5432,
            'name': 'postgres'
        },
        'default_analysis_days': 365,
        'zone_minutes': 30
    }

    try:
        if os.path.exists(config_path):
            with open(config_path, 'r') as file:
                user_config = yaml.safe_load(file)
                default_config.update(user_config)
        return default_config
    except Exception as e:
        print(f"Error loading configuration: {e}")
        return default_config