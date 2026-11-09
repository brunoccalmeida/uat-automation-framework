"""Unit tests for the settings read from the environment (#144)."""

from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from core.config import ConfigurationError, Settings, load_settings
from tests.conftest import SETTINGS_VARIABLES

ROOT = Path(__file__).resolve().parent.parent

pytestmark = pytest.mark.usefixtures("settings_env")


def _workflow_env():
    """Workflow-level variables of the test pipeline."""
    workflow = ROOT / ".github" / "workflows" / "tests.yml"
    return yaml.safe_load(workflow.read_text(encoding="utf-8"))["env"]


def _env_example():
    """Variables of .env.example as a {name: value} dictionary."""
    text = (ROOT / ".env.example").read_text(encoding="utf-8")
    lines = [line for line in text.splitlines() if line and not line.startswith("#")]
    return dict(line.split("=", 1) for line in lines)


class TestRequiredVariables:
    """Fail fast: a run cannot start without what it needs."""

    def test_reads_them_from_the_environment(self):
        settings = load_settings()

        assert settings.base_url == "https://app.example.test"
        assert settings.test_user_password.get_secret_value() == "any_password"

    @pytest.mark.parametrize("variable", ["BASE_URL", "TEST_USER_PASSWORD"])
    def test_missing_one_is_named_in_the_error(self, monkeypatch, variable):
        monkeypatch.delenv(variable)

        with pytest.raises(ConfigurationError, match=variable):
            load_settings()

    @pytest.mark.parametrize("variable", ["BASE_URL", "TEST_USER_PASSWORD"])
    def test_blank_one_counts_as_missing(self, monkeypatch, variable):
        monkeypatch.setenv(variable, "")

        with pytest.raises(ConfigurationError, match=variable):
            load_settings()

    def test_every_missing_variable_is_reported_at_once(self, monkeypatch):
        monkeypatch.delenv("BASE_URL")
        monkeypatch.delenv("TEST_USER_PASSWORD")

        with pytest.raises(ConfigurationError) as error:
            load_settings()

        assert "BASE_URL" in str(error.value)
        assert "TEST_USER_PASSWORD" in str(error.value)


class TestValidation:
    """A wrong value stops the run instead of changing its meaning."""

    @pytest.mark.parametrize(
        "variable, value",
        [
            ("BASE_URL", "not-a-url"),
            ("BASE_URL", "ftp://app.example.test"),
            ("SELENIUM_REMOTE_URL", "not-a-url"),
            ("HEADLESS", "maybe"),
            ("BROWSER", "netscape"),
            ("WINDOW_SIZE", "1920x1080"),
        ],
    )
    def test_invalid_value_is_named_in_the_error(self, monkeypatch, variable, value):
        monkeypatch.setenv(variable, value)

        with pytest.raises(ConfigurationError, match=variable):
            load_settings()

    @pytest.mark.parametrize(
        "value, expected",
        [("true", True), ("1", True), ("yes", True), ("false", False), ("0", False)],
    )
    def test_headless_accepts_the_usual_spellings(self, monkeypatch, value, expected):
        monkeypatch.setenv("HEADLESS", value)

        assert load_settings().headless is expected

    def test_browser_name_is_normalized(self, monkeypatch):
        monkeypatch.setenv("BROWSER", "  FIREFOX ")

        assert load_settings().browser == "firefox"

    def test_url_keeps_its_exact_text(self, monkeypatch):
        """Validated only: a normalizing type would append a trailing slash."""
        monkeypatch.setenv("SELENIUM_REMOTE_URL", " http://localhost:4444 ")

        assert load_settings().selenium_remote_url == "http://localhost:4444"


class TestSecrecy:
    """The password never reaches a log, a report or a traceback."""

    def test_repr_masks_the_password(self):
        assert "any_password" not in repr(load_settings())

    def test_error_does_not_reveal_the_password(self, monkeypatch):
        monkeypatch.setenv("BASE_URL", "not-a-url")

        with pytest.raises(ConfigurationError) as error:
            load_settings()

        assert "any_password" not in str(error.value)

    def test_raw_validation_error_does_not_reveal_the_password(self, monkeypatch):
        """Code that builds Settings directly gets the same protection."""
        monkeypatch.delenv("BASE_URL")

        with pytest.raises(ValidationError) as error:
            # The fields come from the environment, which pyright cannot see.
            Settings()  # pyright: ignore[reportCallIssue]

        assert "any_password" not in str(error.value)

    def test_error_hides_the_validation_details(self, monkeypatch):
        """Chained, the raw error would print in the traceback as well."""
        monkeypatch.delenv("BASE_URL")

        with pytest.raises(ConfigurationError) as error:
            load_settings()

        assert error.value.__suppress_context__


class TestOptionalVariables:
    """What has a sensible value for everyone stays optional."""

    def test_defaults(self):
        settings = load_settings()

        assert settings.browser == "chrome"
        assert settings.headless is True
        assert settings.window_size == "1920,1080"
        assert settings.selenium_remote_url is None

    def test_blank_grid_url_means_a_local_browser(self, monkeypatch):
        monkeypatch.setenv("SELENIUM_REMOTE_URL", "")

        assert load_settings().selenium_remote_url is None


class TestPrecedence:
    """CLI over environment over .env over default."""

    def test_cli_overrides_the_environment(self, monkeypatch):
        monkeypatch.setenv("BROWSER", "chrome")

        assert load_settings(browser="firefox").browser == "firefox"

    def test_absent_cli_value_keeps_the_environment(self, monkeypatch):
        monkeypatch.setenv("BROWSER", "firefox")

        assert load_settings(browser=None).browser == "firefox"

    @pytest.mark.parametrize("blank", ["", "   "])
    def test_blank_cli_value_keeps_the_environment(self, monkeypatch, blank):
        monkeypatch.setenv("BROWSER", "firefox")

        assert load_settings(browser=blank).browser == "firefox"

    def test_environment_overrides_the_dotenv_file(self, settings_env, monkeypatch):
        (settings_env / ".env").write_text("BROWSER=chrome\n", encoding="utf-8")
        monkeypatch.setenv("BROWSER", "firefox")

        assert load_settings().browser == "firefox"

    def test_dotenv_file_supplies_what_the_environment_lacks(
        self, settings_env, monkeypatch
    ):
        monkeypatch.delenv("BASE_URL")
        (settings_env / ".env").write_text(
            "BASE_URL=https://dotenv.example.test\n", encoding="utf-8"
        )

        assert load_settings().base_url == "https://dotenv.example.test"

    def test_typo_in_the_dotenv_file_is_named_in_the_error(self, settings_env):
        """A misspelled name would otherwise leave a default silently in use."""
        (settings_env / ".env").write_text("BROWSR=firefox\n", encoding="utf-8")

        with pytest.raises(ConfigurationError, match="BROWSR"):
            load_settings()


def test_browser_config_is_the_driver_manager_contract(monkeypatch):
    """The keys DriverManager reads, with the resolved values."""
    monkeypatch.setenv("SELENIUM_REMOTE_URL", "http://localhost:4444")

    assert load_settings().browser_config == {
        "name": "chrome",
        "headless": True,
        "window_size": "1920,1080",
        "remote_url": "http://localhost:4444",
    }


class TestCommittedFiles:
    """The committed files stay in step with the settings."""

    def test_list_of_variables_matches_the_settings(self):
        """The isolation fixture must clear every variable there is."""
        assert {name.upper() for name in Settings.model_fields.keys()} == set(
            SETTINGS_VARIABLES
        )

    def test_env_example_documents_every_variable(self):
        assert set(_env_example()) == set(SETTINGS_VARIABLES)

    def test_env_example_has_no_credential(self):
        assert _env_example()["TEST_USER_PASSWORD"] == ""

    def test_ci_sets_every_required_variable(self):
        required = {
            name.upper()
            for name, field in Settings.model_fields.items()
            if field.is_required()
        }

        assert required <= set(_workflow_env())


def test_password_is_not_hardcoded_in_code():
    """Code reads the test password from the settings, never from a literal.

    The CI workflow holds the public demo value, so it is the reference.
    """
    password = _workflow_env()["TEST_USER_PASSWORD"]
    code_files = [
        path
        for folder in ("core", "features", "pages", "scripts", "tests")
        for pattern in ("*.py", "*.feature")
        for path in (ROOT / folder).rglob(pattern)
    ]

    offenders = [
        str(path) for path in code_files if password in path.read_text("utf-8")
    ]

    assert not offenders, f"Read the password from the settings: {offenders}"
