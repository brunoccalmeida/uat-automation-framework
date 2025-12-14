"""Configuration resolution module.

Resolves configuration values from multiple sources with defined priority:
1. CLI parameters (highest priority)
2. Environment variables
3. Config file values (lowest priority)

Uses functional approach - pure functions without side effects.
"""

from typing import Any


def resolve_headless_mode(
    cli_value: str | None,
    env_value: str | None,
    config_value: bool
) -> bool:
    """Resolve headless mode from multiple configuration sources.
    
    Implements configuration hierarchy following 12-factor app principles.
    CLI parameters take precedence over environment variables, which take
    precedence over config file values.
    
    Args:
        cli_value: Value from CLI parameter (-Dheadless=true/false) or None.
        env_value: Value from environment variable (HEADLESS=true/false) or None.
        config_value: Value from config file (config.yaml).
    
    Returns:
        bool: Resolved headless mode value.
        
    Examples:
        >>> resolve_headless_mode("true", None, False)
        True
        >>> resolve_headless_mode(None, "false", True)
        False
        >>> resolve_headless_mode(None, None, True)
        True
        >>> resolve_headless_mode("false", "true", True)
        False
    """
    # Determine effective value using priority hierarchy
    effective_value = cli_value or env_value or str(config_value)
    
    # Convert string to boolean
    return _str_to_bool(effective_value)


def _str_to_bool(value: str) -> bool:
    """Convert string value to boolean.
    
    Accepts multiple formats for flexibility in configuration.
    Case-insensitive comparison.
    
    Args:
        value: String value to convert.
    
    Returns:
        bool: True if value represents truthy value, False otherwise.
        
    Examples:
        >>> _str_to_bool("true")
        True
        >>> _str_to_bool("TRUE")
        True
        >>> _str_to_bool("1")
        True
        >>> _str_to_bool("yes")
        True
        >>> _str_to_bool("false")
        False
        >>> _str_to_bool("anything")
        False
    """
    return value.lower() in ('true', '1', 'yes')


def apply_config_hierarchy(
    config: dict[str, Any],
    key: str,
    cli_value: str | None,
    env_value: str | None
) -> dict[str, Any]:
    """Apply configuration hierarchy for a specific key.
    
    Modifies config dictionary with resolved value following hierarchy.
    
    Args:
        config: Configuration dictionary to modify.
        key: Configuration key to resolve.
        cli_value: Value from CLI parameter or None.
        env_value: Value from environment variable or None.
    
    Returns:
        dict: Modified configuration dictionary (for chaining).
        
    Raises:
        KeyError: If key doesn't exist in config.
    """
    if key == 'headless':
        config[key] = resolve_headless_mode(
            cli_value,
            env_value,
            config.get(key, False)
        )
    
    return config
