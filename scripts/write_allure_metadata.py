#!/usr/bin/env python3
"""Write the Allure Environment and Executor files into a results directory.

Allure reads ``environment.properties`` and ``executor.json`` from the
results directory when it builds the report (allurereport.org/docs, How it
works: "Environment file", "Executor file"); without them the Overview shows
two empty panels (#130).

Every value is read from the run: the Grid's ``/status`` (browser and Grid
versions), the interpreter, the installed Selenium bindings and GitHub's
default variables. ``reportUrl`` is left out on purpose: gh-pages keeps only
the latest report, so a per-build link would point to a newer report.

Usage (CI, after the E2E run): write_allure_metadata.py <results-dir>
Needs SELENIUM_REMOTE_URL and the GITHUB_* default variables.
"""

import json
import os
import platform
import sys
import urllib.request
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path

import selenium


def _fetch_status(url: str) -> dict:
    with urllib.request.urlopen(url, timeout=30) as response:
        return json.load(response)


def environment_properties(
    grid_status: Mapping, python_version: str, selenium_version: str
) -> str:
    """Return the ``environment.properties`` text for the Environment panel."""
    nodes = grid_status["value"]["nodes"]
    if not nodes:
        raise ValueError("the Selenium Grid reported no node")
    node = nodes[0]
    browser = node["slots"][0]["stereotype"]
    # "4.51.0 (revision 35c5fab ...)": the release is what a reader looks for
    grid_version = node["version"].split()[0]
    properties = {
        "Browser": f"{browser['browserName']} {browser['browserVersion']}",
        "Selenium.Grid": grid_version,
        "Selenium.Python": selenium_version,
        "Python": python_version,
    }
    return "".join(f"{key}={value}\n" for key, value in properties.items())


def executor(environ: Mapping[str, str]) -> dict:
    """Return the ``executor.json`` content: the CI run that built the report."""
    run_number = environ["GITHUB_RUN_NUMBER"]
    return {
        "name": "GitHub Actions",
        "type": "github",  # the icon next to the name
        "buildName": f"{environ['GITHUB_WORKFLOW']} #{run_number}",
        "buildOrder": int(run_number),  # labels the trend chart columns
        "buildUrl": (
            f"{environ['GITHUB_SERVER_URL']}/{environ['GITHUB_REPOSITORY']}"
            f"/actions/runs/{environ['GITHUB_RUN_ID']}"
        ),
    }


def main(
    argv: Sequence[str],
    environ: Mapping[str, str],
    fetch_status: Callable[[str], dict] = _fetch_status,
) -> int:
    """Write both files into the results directory given in ``argv``."""
    results = Path(argv[0])
    results.mkdir(parents=True, exist_ok=True)
    status = fetch_status(f"{environ['SELENIUM_REMOTE_URL']}/status")
    (results / "environment.properties").write_text(
        environment_properties(
            status,
            python_version=platform.python_version(),
            selenium_version=selenium.__version__,
        ),
        encoding="utf-8",
    )
    (results / "executor.json").write_text(
        json.dumps(executor(environ), indent=2) + "\n", encoding="utf-8"
    )
    print(f"OK: Allure environment and executor written to {results}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:], os.environ))
