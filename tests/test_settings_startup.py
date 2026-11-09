"""Acceptance tests: a missing variable stops the suites at startup (#144).

These run the real ``behave`` and ``pytest`` in a subprocess, because what is
under test is the startup of each suite: one cannot observe its own start.
The working directory is empty so a developer's ``.env`` cannot supply the
values the test removes.
"""

import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
REMOVED = {"BASE_URL", "TEST_USER_PASSWORD"}
TIMEOUT_SECONDS = 120


def _run(command, cwd):
    """Run a command from cwd with no settings in its environment."""
    environment = {
        name: value for name, value in os.environ.items() if name.upper() not in REMOVED
    }
    environment["PYTHONPATH"] = str(ROOT)
    environment["PYTHONIOENCODING"] = "utf-8"
    return subprocess.run(
        command,
        cwd=cwd,
        env=environment,
        capture_output=True,
        encoding="utf-8",
        timeout=TIMEOUT_SECONDS,
        check=False,
    )


@pytest.mark.parametrize(
    "tool, target, exit_code",
    [
        ("behave", ROOT / "features" / "smoke.feature", 1),
        (
            "pytest",
            ROOT / "tests" / "integration" / "test_login_page_integration.py",
            pytest.ExitCode.USAGE_ERROR,
        ),
    ],
    ids=["behave", "pytest"],
)
def test_suite_stops_at_startup_naming_the_missing_variable(
    tmp_path, tool, target, exit_code
):
    """No browser opens: the run ends with an error that names the variable."""
    result = _run([sys.executable, "-m", tool, str(target)], tmp_path)
    output = result.stdout + result.stderr

    assert result.returncode == exit_code, output
    assert "BASE_URL" in output, output
    assert "TEST_USER_PASSWORD" in output, output


def test_listing_the_tests_needs_no_settings(tmp_path):
    """Only running opens a browser: the README metrics hook just collects."""
    target = ROOT / "tests" / "integration" / "test_login_page_integration.py"

    result = _run([sys.executable, "-m", "pytest", "--co", "-q", str(target)], tmp_path)

    assert result.returncode == 0, result.stdout + result.stderr
