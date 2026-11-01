"""Unit tests for configuration accessors."""

from pathlib import Path

from core.config import get_default_password, load_config


def test_get_default_password_reads_remote_environment():
    """get_default_password should return the configured test password."""
    config = {"environment": {"remote": {"default_password": "any_password"}}}

    assert get_default_password(config) == "any_password"


def test_password_is_not_hardcoded_outside_config():
    """Code reads the test password from config.yaml, never from a literal."""
    password = get_default_password(load_config("config.yaml"))
    code_files = [
        path
        for folder in ("core", "features", "pages", "scripts", "tests")
        for pattern in ("*.py", "*.feature")
        for path in Path(folder).rglob(pattern)
    ]

    offenders = [
        str(path) for path in code_files if password in path.read_text("utf-8")
    ]

    assert not offenders, f"Read the password from config instead: {offenders}"
