"""Shared assertion for the navigation contract of page objects.

Sauce Demo is a SPA: the URL changes before the destination renders. So a
navigation method must click, build the destination page and return it only
after ``wait_until_loaded``, in this order (deterministic guard of the race
covered by tests/integration/test_navigation_integration.py).
"""

from unittest.mock import Mock, patch


def assert_clicks_then_returns_loaded(page, navigate, locator, destination):
    """Assert ``navigate()`` clicks ``locator`` and returns the loaded page.

    Args:
        page: Page object under test (its ``click`` is mocked).
        navigate: Bound navigation method of ``page``, called with no args.
        locator: Locator the method must click.
        destination: Dotted path of the destination page class to mock.
    """
    with (
        patch.object(page, "click") as mock_click,
        patch(destination) as mock_next,
    ):
        calls = Mock()
        calls.attach_mock(mock_click, "click")
        calls.attach_mock(mock_next, "destination")
        result = navigate()

    mock_click.assert_called_once_with(locator)
    mock_next.assert_called_once_with(page.driver)
    assert [c[0] for c in calls.mock_calls] == [
        "click",
        "destination",
        "destination().wait_until_loaded",
    ]
    assert result is mock_next.return_value.wait_until_loaded.return_value
