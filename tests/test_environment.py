"""Unit tests for the Behave lifecycle hooks."""

import json
from types import SimpleNamespace
from unittest.mock import Mock, call, patch

import pytest
from behave.model_core import Status
from selenium.common.exceptions import WebDriverException

from features.environment import after_scenario, before_all, before_scenario

URL = "https://www.saucedemo.com/inventory.html"
JS_ERROR = {"type_": "javascript", "level": "error", "text": "Error: boom"}


def _context(page_errors=None):
    """Context with a live driver, as before_scenario leaves it."""
    driver = Mock(current_url=URL)
    driver.get_screenshot_as_png.return_value = b"png"
    return SimpleNamespace(
        driver=driver,
        driver_manager=Mock(),
        page_errors=[] if page_errors is None else page_errors,
    )


def _page_errors_call(allure, errors):
    """The Allure attachment of the page errors, as after_scenario makes it."""
    return call(
        json.dumps(errors, indent=2),
        name="page-errors",
        attachment_type=allure.attachment_type.JSON,
    )


@pytest.mark.parametrize("status", [Status.failed, Status.error])
@patch("features.environment.allure")
def test_failed_scenario_attaches_page_errors_screenshot_and_url(allure, status):
    """A failed (assertion) or broken (exception) scenario keeps its evidence.

    The page errors come first: they are already in hand, so a browser that
    cannot answer the screenshot must not cost them too.
    """
    context = _context([JS_ERROR])

    after_scenario(context, Mock(status=status))

    assert allure.attach.call_args_list == [
        _page_errors_call(allure, [JS_ERROR]),
        call(b"png", name="screenshot", attachment_type=allure.attachment_type.PNG),
        call(URL, name="url", attachment_type=allure.attachment_type.URI_LIST),
    ]


@patch("features.environment.allure")
def test_failed_scenario_attaches_an_empty_page_error_list(allure):
    """'[]' is evidence too: no JavaScript error rules out a cause (#183)."""
    after_scenario(_context([]), Mock(status=Status.failed))

    assert allure.attach.call_args_list[0] == _page_errors_call(allure, [])


@patch("features.environment.allure")
def test_page_errors_survive_a_browser_that_cannot_answer(allure):
    """A crashed tab loses the screenshot, not the errors already heard."""
    context = _context([JS_ERROR])
    context.driver.get_screenshot_as_png.side_effect = WebDriverException("crash")

    with pytest.raises(WebDriverException):
        after_scenario(context, Mock(status=Status.failed))

    assert allure.attach.call_args_list == [_page_errors_call(allure, [JS_ERROR])]


@patch("features.environment.allure")
def test_screenshot_survives_a_listener_that_never_started(allure):
    """The driver opened but watch_page_errors raised: keep what there is."""
    context = _context()
    del context.page_errors

    after_scenario(context, Mock(status=Status.hook_error))

    assert [c.kwargs["name"] for c in allure.attach.call_args_list] == [
        "screenshot",
        "url",
    ]


@patch("features.environment.watch_page_errors")
@patch("features.environment.DriverManager")
@pytest.mark.usefixtures("settings_env")
def test_before_scenario_listens_to_page_errors_from_the_start(
    driver_manager, watch_page_errors
):
    """The listener is on before the first step navigates (#183).

    An app bundle that throws does so while the first page loads; a listener
    added later would miss it.
    """
    context = _before_context({})
    before_all(context)

    before_scenario(context, Mock())

    driver = driver_manager.return_value.get_driver.return_value
    watch_page_errors.assert_called_once_with(driver)
    assert context.page_errors is watch_page_errors.return_value


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


def _before_context(userdata):
    """Context as Behave hands it to before_all."""
    return SimpleNamespace(config=SimpleNamespace(userdata=userdata))


@pytest.mark.parametrize(
    ("userdata", "env", "expected"),
    [
        ({"remote_url": "http://cli:4444"}, "http://env:4444", "http://cli:4444"),
        ({}, "http://env:4444", "http://env:4444"),
        ({}, None, None),
    ],
    ids=["cli-wins", "env", "local-default"],
)
@patch("features.environment.DriverManager")
@pytest.mark.usefixtures("settings_env")
def test_before_scenario_passes_grid_url_to_driver_manager(
    driver_manager, monkeypatch, userdata, env, expected
):
    """E2E and smoke open their sessions in the configured Grid (#116).

    CI runners also ship local browsers, so without this wiring the Behave
    suites would pass while silently skipping the container.
    """
    if env:
        monkeypatch.setenv("SELENIUM_REMOTE_URL", env)
    context = _before_context(userdata)

    before_all(context)
    before_scenario(context, Mock())

    assert driver_manager.call_args.args[0]["remote_url"] == expected


@pytest.mark.parametrize(
    "userdata, attribute, expected",
    [
        ({"browser": "firefox"}, "browser", "firefox"),
        ({"headless": "false"}, "headless", False),
    ],
    ids=["browser", "headless"],
)
@pytest.mark.usefixtures("settings_env")
def test_before_all_applies_the_cli_parameters(userdata, attribute, expected):
    """-Dbrowser and -Dheadless reach the settings."""
    context = _before_context(userdata)

    before_all(context)

    assert getattr(context.settings, attribute) == expected
