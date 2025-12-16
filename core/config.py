"""Configuration management module.

Provides functions to load and access configuration from YAML files.
Uses functional approach for stateless configuration loading.
"""

from pathlib import Path
from typing import Any

import yaml


def load_config(config_path: str = "config.yaml") -> dict[str, Any]:
    """Load configuration from YAML file.

    Args:
        config_path: Path to the YAML configuration file.

    Returns:
        Dictionary containing the configuration.

    Raises:
        FileNotFoundError: If configuration file doesn't exist.
        yaml.YAMLError: If YAML is malformed.
    """
    path = Path(config_path)

    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(path, encoding="utf-8") as f:
        config = yaml.safe_load(f)

    return config


def get_base_url(config: dict[str, Any]) -> str:
    """Extract base URL from configuration.

    Args:
        config: Configuration dictionary.

    Returns:
        Base URL for the application under test.
    """
    return config["environment"]["remote"]["base_url"]


def get_browser_config(config: dict[str, Any]) -> dict[str, Any]:
    """Extract browser configuration.

    Args:
        config: Configuration dictionary.

    Returns:
        Browser configuration dictionary.
    """
    return config["browser"]
