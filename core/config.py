"""Settings read from the environment (Twelve-Factor App, factor III).

Precedence, highest first: CLI arguments, environment variables, the ``.env``
file in the working directory, defaults. Everything is validated once, at
startup, so a wrong setting stops the run with a message that names it.
"""

from typing import Annotated, Any, Literal

from pydantic import (
    AfterValidator,
    Field,
    HttpUrl,
    SecretStr,
    TypeAdapter,
    ValidationError,
    field_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict

_HTTP_URL_ADAPTER = TypeAdapter(HttpUrl)


class ConfigurationError(Exception):
    """A setting is missing or invalid."""


def _validate_http_url(value: str) -> str:
    """Accept only http(s) URLs, returning the text unchanged.

    ``HttpUrl`` itself would normalize the value (trailing slash), changing
    the address the browser opens.
    """
    try:
        _HTTP_URL_ADAPTER.validate_python(value)
    except ValidationError as error:
        raise ValueError("must be an http or https URL") from error
    return value


_Url = Annotated[str, AfterValidator(_validate_http_url)]


class Settings(BaseSettings):
    """The variables a run depends on; each field is one variable."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        str_strip_whitespace=True,
        hide_input_in_errors=True,
    )

    base_url: _Url
    test_user_password: SecretStr
    browser: Literal["chrome", "firefox"] = "chrome"
    headless: bool = True
    window_size: str = Field(default="1920,1080", pattern=r"^\d+,\d+$")
    selenium_remote_url: _Url | None = None

    @field_validator("browser", mode="before")
    @classmethod
    def _normalize_browser(cls, value: str) -> str:
        return value.strip().lower()

    @property
    def browser_config(self) -> dict[str, Any]:
        """Browser settings in the form DriverManager reads."""
        return {
            "name": self.browser,
            "headless": self.headless,
            "window_size": self.window_size,
            "remote_url": self.selenium_remote_url,
        }


def load_settings(**cli_overrides: str | None) -> Settings:
    """Read and validate the settings.

    Args:
        **cli_overrides: Field values from the command line. A value that was
            not given (None or blank) leaves the field to the other sources.

    Returns:
        The validated settings.

    Raises:
        ConfigurationError: If a setting is missing or invalid, naming every
            variable at fault and never showing a value.
    """
    # Any: the command line only has text, which the validation converts.
    overrides: dict[str, Any] = {
        name: value for name, value in cli_overrides.items() if value and value.strip()
    }
    try:
        return Settings(**overrides)
    except ValidationError as error:
        problems = "\n".join(
            f"  {str(item['loc'][0]).upper()}: {item['msg']}"
            for item in error.errors(include_input=False, include_url=False)
        )
        raise ConfigurationError(
            f"Invalid configuration (see .env.example):\n{problems}"
        ) from None
