"""Unit tests for the Behave lifecycle hooks."""

from types import SimpleNamespace
from unittest.mock import Mock, call, patch

import pytest
from behave.model_core import Status
from selenium.common.exceptions import WebDriverException

from features.environment import after_scenario

URL = "https://www.saucedemo.com/inventory.html"


def _context():
    """Context with a live driver, as before_scenario leaves it."""
    driver = Mock(current_url=URL)
    driver.get_screenshot_as_png.return_value = b"png"
    return SimpleNamespace(driver=driver, driver_manager=Mock())


@pytest.mark.parametrize("status", [Status.failed, Status.error])
@patch("features.environment.allure")
def test_failed_scenario_attaches_screenshot_and_url(allure, status):
    """A failed (assertion) or broken (exception) scenario keeps its evidence."""
    context = _context()

    after_scenario(context, Mock(status=status))

    assert allure.attach.call_args_list == [
        call(b"png", name="screenshot", attachment_type=allure.attachment_type.PNG),
        call(URL, name="url", attachment_type=allure.attachment_type.URI_LIST),
    ]


@patch("features.environment.allure")
def test_passed_scenario_attaches_nothing(allure):
    """Evidence only where it explains a failure; passing runs stay lean."""
    after_scenario(_context(), Mock(status=Status.passed))

    allure.attach.assert_not_called()


@patch("features.environment.allure")
def test_evidence_is_taken_before_the_browser_quits(allure):
    """After quit there is no page left to capture."""
    context = _context()
    order = Mock()
    order.attach_mock(allure.attach, "attach")
    order.attach_mock(context.driver_manager.quit, "quit")

    after_scenario(context, Mock(status=Status.failed))

    assert order.mock_calls[-1] == call.quit()
    assert call.quit() not in order.mock_calls[:-1]


@patch("features.environment.allure", Mock())
def test_browser_quits_even_when_capture_fails():
    """A hung browser must not leak; the capture error still surfaces."""
    context = _context()
    context.driver.get_screenshot_as_png.side_effect = WebDriverException("hung")

    with pytest.raises(WebDriverException):
        after_scenario(context, Mock(status=Status.failed))

    context.driver_manager.quit.assert_called_once()


@patch("features.environment.allure")
def test_no_capture_when_driver_was_never_created(allure):
    """before_scenario failed (hook_error): there is no page to capture."""
    after_scenario(SimpleNamespace(), Mock(status=Status.hook_error))

    allure.attach.assert_not_called()
