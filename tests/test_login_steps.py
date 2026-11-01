"""Unit tests for login step definitions.

Tests the step definition logic in isolation, particularly the error message
verification with OR logic support.
"""

from unittest.mock import Mock, patch

import pytest

# Import the step functions we want to test
from features.steps.login_steps import (
    step_log_in_as,
    step_logged_in_as_user,
    step_verify_error_contains,
)

CONFIG = {
    "environment": {
        "remote": {"base_url": "https://example.test", "default_password": "pw"}
    }
}


class TestStepVerifyErrorContains:
    """Test the error message verification step with OR logic support."""

    def test_simple_text_match_success(self):
        """Should pass when simple text is found in error message."""
        context = Mock()
        context.login_page.get_error_message.return_value = (
            "Epic sadface: Username is required"
        )

        # Should not raise assertion
        step_verify_error_contains(context, "Username is required")

    def test_simple_text_match_case_insensitive(self):
        """Should match text case-insensitively."""
        context = Mock()
        context.login_page.get_error_message.return_value = (
            "Epic sadface: USERNAME IS REQUIRED"
        )

        # Should not raise assertion (case-insensitive)
        step_verify_error_contains(context, "username is required")

    def test_simple_text_match_failure(self):
        """Should fail when simple text is not found in error message."""
        context = Mock()
        context.login_page.get_error_message.return_value = (
            "Epic sadface: Password is required"
        )

        with pytest.raises(AssertionError) as exc_info:
            step_verify_error_contains(context, "Username is required")

        assert "Error message should mention 'Username is required'" in str(
            exc_info.value
        )

    def test_or_logic_first_alternative_matches(self):
        """Should pass when first alternative text is found."""
        context = Mock()
        context.login_page.get_error_message.return_value = (
            "Epic sadface: User is locked out"
        )

        # Should not raise assertion (first alternative matches)
        step_verify_error_contains(context, 'locked out" or "too many attempts')

    def test_or_logic_second_alternative_matches(self):
        """Should pass when second alternative text is found."""
        context = Mock()
        context.login_page.get_error_message.return_value = (
            "Epic sadface: Too many failed attempts"
        )

        # Should not raise assertion (second alternative matches "failed attempts")
        step_verify_error_contains(context, 'locked out" or "failed attempts')

    def test_or_logic_no_alternative_matches(self):
        """Should fail when no alternative text is found."""
        context = Mock()
        context.login_page.get_error_message.return_value = (
            "Epic sadface: Invalid credentials"
        )

        with pytest.raises(AssertionError) as exc_info:
            step_verify_error_contains(context, 'locked out" or "too many attempts')

        error_message = str(exc_info.value)
        assert "Error message should mention one of" in error_message
        assert "locked out" in error_message
        assert "too many attempts" in error_message

    def test_or_logic_case_insensitive(self):
        """Should match OR alternatives case-insensitively."""
        context = Mock()
        context.login_page.get_error_message.return_value = "Epic sadface: LOCKED OUT"

        # Should not raise assertion (case-insensitive match)
        step_verify_error_contains(context, 'locked out" or "too many attempts')

    def test_or_logic_with_multiple_alternatives(self):
        """Should handle multiple alternatives (more than 2)."""
        context = Mock()
        context.login_page.get_error_message.return_value = (
            "Epic sadface: Account suspended"
        )

        # Should not raise assertion (third alternative matches)
        step_verify_error_contains(
            context, 'locked out" or "banned" or "suspended" or "disabled'
        )

    def test_or_logic_partial_match_within_message(self):
        """Should match alternatives as substrings within error message."""
        context = Mock()
        context.login_page.get_error_message.return_value = (
            "Epic sadface: Username and password do not match any user"
        )

        # Should not raise assertion ("do not match" is substring)
        step_verify_error_contains(context, 'invalid" or "do not match')


class TestLoginStepsUseConfiguredPassword:
    """Login steps take the password from config, not from a literal."""

    def test_log_in_as_uses_configured_password(self):
        """Should log in with the scenario's user and the configured password."""
        context = Mock(config_data=CONFIG)

        step_log_in_as(context, "standard_user")

        context.login_page.login.assert_called_once_with("standard_user", "pw")

    def test_logged_in_as_uses_configured_password(self):
        """Should open the app and log in with the configured password."""
        context = Mock(config_data=CONFIG)

        with patch("features.steps.login_steps.LoginPage") as login_page_cls:
            step_logged_in_as_user(context, "problem_user")

        login_page_cls.return_value.login.assert_called_once_with("problem_user", "pw")
