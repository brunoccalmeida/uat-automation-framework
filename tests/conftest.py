"""Fixtures shared by the unit tests."""

import pytest

SETTINGS_VARIABLES = (
    "BASE_URL",
    "TEST_USER_PASSWORD",
    "BROWSER",
    "HEADLESS",
    "WINDOW_SIZE",
    "SELENIUM_REMOTE_URL",
)


@pytest.fixture(name="settings_env")
def fixture_settings_env(monkeypatch, tmp_path):
    """Valid required settings, isolated from the machine running the test.

    The settings come from the process environment and from a ``.env`` in the
    working directory: both would otherwise make the result depend on who
    runs the test.

    Returns:
        The empty working directory, for tests that write a ``.env``.
    """
    monkeypatch.chdir(tmp_path)
    for name in SETTINGS_VARIABLES:
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("BASE_URL", "https://app.example.test")
    monkeypatch.setenv("TEST_USER_PASSWORD", "any_password")
    return tmp_path
