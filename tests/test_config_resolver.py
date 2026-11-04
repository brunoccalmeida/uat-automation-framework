"""Tests for configuration resolution logic.

Validates configuration hierarchy and value conversion following TDD principles.
"""

import pytest

from core.config_resolver import (
    _str_to_bool,
    apply_config_hierarchy,
    resolve_browser_name,
    resolve_headless_mode,
    resolve_remote_url,
)


class TestResolveHeadlessMode:
    """Test headless mode resolution with configuration hierarchy."""

    def test_cli_parameter_has_highest_priority(self):
        """CLI parameter should override environment and config values."""
        result = resolve_headless_mode(
            cli_value="true", env_value="false", config_value=False
        )
        assert result is True

        result = resolve_headless_mode(
            cli_value="false", env_value="true", config_value=True
        )
        assert result is False

    def test_env_variable_overrides_config(self):
        """Environment variable should override config file when CLI not set."""
        result = resolve_headless_mode(
            cli_value=None, env_value="true", config_value=False
        )
        assert result is True

        result = resolve_headless_mode(
            cli_value=None, env_value="false", config_value=True
        )
        assert result is False

    def test_config_file_is_fallback(self):
        """Config file value should be used when CLI and ENV not set."""
        result = resolve_headless_mode(
            cli_value=None, env_value=None, config_value=True
        )
        assert result is True

        result = resolve_headless_mode(
            cli_value=None, env_value=None, config_value=False
        )
        assert result is False

    def test_empty_string_cli_falls_through_to_env(self):
        """Empty string CLI value should fall through to environment variable."""
        result = resolve_headless_mode(
            cli_value="", env_value="true", config_value=False
        )
        assert result is True

    def test_empty_string_env_falls_through_to_config(self):
        """Empty string ENV value should fall through to config."""
        result = resolve_headless_mode(cli_value=None, env_value="", config_value=True)
        assert result is True


class TestStrToBool:
    """Test string to boolean conversion."""

    @pytest.mark.parametrize(
        "value,expected",
        [
            ("true", True),
            ("True", True),
            ("TRUE", True),
            ("1", True),
            ("yes", True),
            ("Yes", True),
            ("YES", True),
        ],
    )
    def test_truthy_values(self, value, expected):
        """Various truthy string values should convert to True."""
        assert _str_to_bool(value) is expected

    @pytest.mark.parametrize(
        "value,expected",
        [
            ("false", False),
            ("False", False),
            ("FALSE", False),
            ("0", False),
            ("no", False),
            ("No", False),
            ("NO", False),
            ("anything", False),
            ("", False),
            ("random", False),
        ],
    )
    def test_falsy_values(self, value, expected):
        """Various falsy string values should convert to False."""
        assert _str_to_bool(value) is expected


class TestApplyConfigHierarchy:
    """Test applying configuration hierarchy to config dictionary."""

    def test_apply_headless_with_cli_override(self):
        """Should apply CLI override to config dictionary."""
        config = {"headless": False}
        result = apply_config_hierarchy(
            config, key="headless", cli_value="true", env_value=None
        )

        assert result["headless"] is True
        assert result is config  # Should modify in place

    def test_apply_headless_with_env_override(self):
        """Should apply ENV override when CLI not set."""
        config = {"headless": False}
        result = apply_config_hierarchy(
            config, key="headless", cli_value=None, env_value="true"
        )

        assert result["headless"] is True

    def test_apply_headless_with_config_default(self):
        """Should use config default when no overrides."""
        config = {"headless": True}
        result = apply_config_hierarchy(
            config, key="headless", cli_value=None, env_value=None
        )

        assert result["headless"] is True

    def test_handles_missing_headless_key(self):
        """Should handle missing headless key with False default."""
        config = {}
        result = apply_config_hierarchy(
            config, key="headless", cli_value=None, env_value=None
        )

        assert result["headless"] is False

    def test_apply_browser_name_with_cli_override(self):
        """Should apply CLI browser override to config dictionary."""
        config = {"name": "chrome"}
        result = apply_config_hierarchy(
            config, key="name", cli_value="firefox", env_value=None
        )

        assert result["name"] == "firefox"
        assert result is config  # Should modify in place

    def test_apply_browser_name_with_env_override(self):
        """Should apply ENV browser override when CLI not set."""
        config = {"name": "chrome"}
        result = apply_config_hierarchy(
            config, key="name", cli_value=None, env_value="firefox"
        )

        assert result["name"] == "firefox"

    def test_apply_browser_name_defaults_to_config_value(self):
        """Should use config value when no overrides are provided."""
        config = {"name": "chrome"}
        result = apply_config_hierarchy(
            config, key="name", cli_value=None, env_value=None
        )

        assert result["name"] == "chrome"

    def test_apply_browser_name_handles_missing_key(self):
        """Should default browser name to chrome when missing."""
        config = {}
        result = apply_config_hierarchy(
            config, key="name", cli_value=None, env_value=None
        )

        assert result["name"] == "chrome"


class TestResolveBrowserName:
    """Test browser name resolution with configuration hierarchy."""

    def test_cli_parameter_has_highest_priority(self):
        """CLI parameter should override environment and config values."""
        result = resolve_browser_name(
            cli_value="firefox", env_value="chrome", config_value="chrome"
        )
        assert result == "firefox"

    def test_env_variable_overrides_config(self):
        """Environment variable should override config file when CLI not set."""
        result = resolve_browser_name(
            cli_value=None, env_value="firefox", config_value="chrome"
        )
        assert result == "firefox"

    def test_config_file_is_fallback(self):
        """Config file value should be used when CLI and ENV not set."""
        result = resolve_browser_name(
            cli_value=None, env_value=None, config_value="firefox"
        )
        assert result == "firefox"

    def test_empty_string_cli_falls_through_to_env(self):
        """Empty string CLI value should fall through to environment variable."""
        result = resolve_browser_name(
            cli_value="", env_value="firefox", config_value="chrome"
        )
        assert result == "firefox"

    def test_empty_string_env_falls_through_to_config(self):
        """Empty string ENV value should fall through to config."""
        result = resolve_browser_name(
            cli_value=None, env_value="", config_value="firefox"
        )
        assert result == "firefox"

    def test_normalizes_case_and_whitespace(self):
        """Should normalize browser name to lowercase and strip whitespace."""
        result = resolve_browser_name(
            cli_value="  FIREFOX ", env_value=None, config_value="chrome"
        )
        assert result == "firefox"


class TestRealWorldScenarios:
    """Test real-world usage scenarios."""

    def test_local_development_scenario(self):
        """Developer runs tests with config.yaml default."""
        result = resolve_headless_mode(
            cli_value=None,
            env_value=None,
            config_value=False,  # config.yaml has headless: false
        )
        assert result is False  # Browser should be visible

    def test_ci_cd_scenario(self):
        """CI/CD pipeline sets HEADLESS=true environment variable."""
        result = resolve_headless_mode(
            cli_value=None,
            env_value="true",  # export HEADLESS=true in CI
            config_value=False,
        )
        assert result is True  # Browser should be headless

    def test_debug_in_ci_scenario(self):
        """Developer forces visible browser in CI for debugging."""
        result = resolve_headless_mode(
            cli_value="false",  # -Dheadless=false overrides CI
            env_value="true",  # CI has HEADLESS=true
            config_value=False,
        )
        assert result is False  # Browser should be visible for debugging

    def test_quick_headless_test_locally(self):
        """Developer tests headless mode before commit."""
        result = resolve_headless_mode(
            cli_value="true",  # -Dheadless=true for quick test
            env_value=None,
            config_value=False,
        )
        assert result is True  # Browser should be headless


class TestResolveRemoteUrl:
    """Test remote WebDriver URL resolution (#116).

    No value anywhere is legitimate: it means a local browser.
    """

    def test_cli_parameter_has_highest_priority(self):
        """CLI should override ENV and config."""
        result = resolve_remote_url("http://cli:4444", "http://env:4444", None)

        assert result == "http://cli:4444"

    def test_env_variable_overrides_config(self):
        """ENV should override config when CLI is not set."""
        result = resolve_remote_url(None, "http://env:4444", "http://cfg:4444")

        assert result == "http://env:4444"

    def test_config_file_is_fallback(self):
        """Config value is used when CLI and ENV are not set."""
        result = resolve_remote_url(None, None, "http://cfg:4444")

        assert result == "http://cfg:4444"

    def test_no_value_anywhere_means_local_browser(self):
        """None everywhere resolves to None (local driver)."""
        assert resolve_remote_url(None, None, None) is None

    @pytest.mark.parametrize("blank", ["", "   "])
    def test_blank_value_falls_through(self, blank):
        """A blank value (e.g. SELENIUM_REMOTE_URL=) is the same as unset."""
        assert resolve_remote_url(blank, blank, None) is None

    def test_strips_surrounding_whitespace(self):
        """Whitespace around the URL is not part of it."""
        result = resolve_remote_url(None, " http://env:4444 ", None)

        assert result == "http://env:4444"

    def test_apply_config_hierarchy_sets_remote_url(self):
        """apply_config_hierarchy resolves the remote_url key in place."""
        config = {}
        result = apply_config_hierarchy(
            config, key="remote_url", cli_value=None, env_value="http://env:4444"
        )

        assert result["remote_url"] == "http://env:4444"
