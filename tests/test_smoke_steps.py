"""Unit tests for smoke step definitions."""

from unittest.mock import Mock, patch

from pydantic import SecretStr

from features.steps.smoke_steps import step_enter_valid_credentials

SETTINGS = Mock(test_user_password=SecretStr("pw"))


def test_enter_valid_credentials_uses_configured_password():
    """Should log in as standard_user with the configured password."""
    context = Mock(settings=SETTINGS)

    with patch("features.steps.smoke_steps.LoginPage") as login_page_cls:
        step_enter_valid_credentials(context)

    login_page_cls.return_value.login.assert_called_once_with("standard_user", "pw")
