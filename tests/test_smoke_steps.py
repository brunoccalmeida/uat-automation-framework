"""Unit tests for smoke step definitions."""

from unittest.mock import Mock

from features.steps.smoke_steps import step_enter_valid_credentials

CONFIG = {"environment": {"remote": {"default_password": "pw"}}}


def test_enter_valid_credentials_uses_configured_password():
    """Should log in as standard_user with the configured password."""
    context = Mock(config_data=CONFIG)

    step_enter_valid_credentials(context)

    context.login_page.login.assert_called_once_with("standard_user", "pw")
