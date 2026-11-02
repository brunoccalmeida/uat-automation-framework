"""Unit tests for smoke step definitions."""

from unittest.mock import Mock, patch

from features.steps.smoke_steps import step_enter_valid_credentials

CONFIG = {"environment": {"remote": {"default_password": "pw"}}}


def test_enter_valid_credentials_uses_configured_password():
    """Should log in as standard_user with the configured password."""
    context = Mock(config_data=CONFIG)

    with patch("features.steps.smoke_steps.LoginPage") as login_page_cls:
        step_enter_valid_credentials(context)

    login_page_cls.return_value.login.assert_called_once_with("standard_user", "pw")
