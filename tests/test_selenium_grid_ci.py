"""Browser tests run in docker-selenium, defined once in compose.yaml (#116).

Local runs and CI share one browser build only if both start the same
container definition (12-factor X, dev/prod parity). compose.yaml is that
single source; the checks:

- full tag plus digest: a tag is a movable pointer (docker-selenium README,
  "Always use a Docker image with a full tag"; digest as for Actions by SHA);
- ``shm_size``: the README asks for it on every image with a browser;
- a health check: ``docker compose up --wait`` returns only once the Grid
  is ready, so tests never start against a Grid still booting;
- the browser jobs start the Grid through Compose (no copy of the image in
  the workflow) and point SELENIUM_REMOTE_URL at it;
- Dependabot watches compose.yaml, so the pinned digest does not go stale;
- the integration suite runs in every supported browser (#118).
"""

import re
from pathlib import Path

import pytest
import yaml

from core.config import Settings

ROOT = Path(__file__).resolve().parent.parent
COMPOSE = ROOT / "compose.yaml"
WORKFLOW = ROOT / ".github" / "workflows" / "tests.yml"
DEPENDABOT = ROOT / ".github" / "dependabot.yml"
BROWSERS = ("chrome", "firefox")
BROWSER_JOBS = ("smoke-matrix", "test", "integration-matrix")
PINNED_IMAGE = re.compile(
    r"^selenium/standalone-(?P<browser>chrome|firefox)"
    r":\d+\.\d+\.\d+-\d{8}@sha256:[0-9a-f]{64}$"
)
MATRIX_EXPRESSION = re.compile(r"\$\{\{\s*matrix\.(?P<key>[\w-]+)\s*\}\}")


def _load(path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


SERVICES = _load(COMPOSE)["services"]
JOBS = _load(WORKFLOW)["jobs"]
DEFAULT_BROWSER = Settings.model_construct().browser


def _host_port(browser):
    """Host port that publishes the Grid port (4444) of the service."""
    for mapping in SERVICES[browser]["ports"]:
        host, container = str(mapping).split(":")
        if container == "4444":
            return host
    raise AssertionError(f"compose service '{browser}' does not publish 4444")


def _variants(job_name):
    """Return one dict of matrix values per variant (a single one if none)."""
    matrix = JOBS[job_name].get("strategy", {}).get("matrix", {})
    return matrix.get("include", [{}])


def _resolve(text, variant):
    """Replace ${{ matrix.x }} expressions with the variant's values."""
    return MATRIX_EXPRESSION.sub(lambda m: str(variant[m.group("key")]), text)


def _compose_up_browser(job_name, variant):
    """Browser the job starts with 'docker compose up --wait', if any."""
    for step in JOBS[job_name]["steps"]:
        run = _resolve(step.get("run", ""), variant)
        found = re.search(r"docker compose up --wait\b.*?\b(chrome|firefox)\b", run)
        if found:
            return found.group(1)
    return None


def _integration_runs():
    """Yield (job, variant, browser used, Grid started) per integration run.

    The browser used is what the helper reads (#118): BROWSER from the step
    or job env, else the default in Settings.
    """
    for job_name, job in JOBS.items():
        for variant in _variants(job_name):
            for step in job.get("steps", []):
                if "pytest tests/integration" not in step.get("run", ""):
                    continue
                env = {**job.get("env", {}), **step.get("env", {})}
                used = _resolve(str(env.get("BROWSER", DEFAULT_BROWSER)), variant)
                yield job_name, variant, used, _compose_up_browser(job_name, variant)


def test_integration_suite_runs_in_every_supported_browser():
    """Page Objects are checked against each browser's driver, not only Chrome.

    MDN ("Strategies for carrying out testing"): a supported, common browser
    is tested thoroughly; the README supports Chrome and Firefox.
    """
    assert {used for _, _, used, _ in _integration_runs()} == set(BROWSERS)


def test_integration_runs_in_the_browser_of_its_grid():
    """A job that starts Firefox's Grid must ask the helper for Firefox."""
    for job_name, variant, used, grid in _integration_runs():
        assert used == grid, f"{job_name} {variant}: uses {used}, Grid is {grid}"


@pytest.mark.parametrize("browser", BROWSERS)
class TestComposeService:
    """compose.yaml defines one pinned, ready-checked Grid per browser."""

    def test_image_is_pinned_and_matches_the_browser(self, browser):
        image = SERVICES[browser]["image"]
        pinned = PINNED_IMAGE.match(image)

        assert pinned, f"'{image}' is not full tag + digest"
        assert pinned.group("browser") == browser

    def test_sets_shared_memory(self, browser):
        assert SERVICES[browser]["shm_size"] == "2gb"

    def test_health_check_asks_the_grid(self, browser):
        assert "/opt/bin/check-grid.sh" in SERVICES[browser]["healthcheck"]["test"]

    def test_publishes_grid_port(self, browser):
        assert _host_port(browser).isdigit()


def test_browsers_share_one_grid_version():
    """Chrome and Firefox images come from the same docker-selenium release."""
    tags = {SERVICES[b]["image"].split(":")[1].split("@")[0] for b in BROWSERS}

    assert len(tags) == 1, tags


@pytest.mark.parametrize("job_name", BROWSER_JOBS)
class TestBrowserJobUsesCompose:
    """Each browser job starts its Grid from compose.yaml and points at it."""

    def test_has_no_container_of_its_own(self, job_name):
        """A workflow copy of the image would drift from compose.yaml."""
        assert "services" not in JOBS[job_name]

    def test_starts_grid_with_compose_and_points_at_it(self, job_name):
        for variant in _variants(job_name):
            browser = _compose_up_browser(job_name, variant)
            assert browser, f"{job_name} {variant}: no 'docker compose up --wait'"
            assert browser == variant.get("browser", "chrome")

            url = _resolve(JOBS[job_name]["env"]["SELENIUM_REMOTE_URL"], variant)
            assert url == f"http://localhost:{_host_port(browser)}"


def test_dependabot_updates_compose_images():
    """Without updates a digest pin goes stale and gathers browser CVEs."""
    ecosystems = {u["package-ecosystem"] for u in _load(DEPENDABOT)["updates"]}

    assert "docker-compose" in ecosystems


def test_dependabot_stays_in_the_grid_tag_family():
    """Only Grid-family tags (4.x) may be proposed (#121).

    docker-selenium also tags each image by browser version, and Dependabot
    compares tags as SemVer: #120 proposed chrome 155.0.8059.39 and firefox
    157.0 (a browser downgrade) over 4.51.0. Ignoring majors for selenium/*
    drops those families; a Grid major stays a human decision.
    """
    compose = next(
        u
        for u in _load(DEPENDABOT)["updates"]
        if u["package-ecosystem"] == "docker-compose"
    )

    assert {
        "dependency-name": "selenium/*",
        "update-types": ["version-update:semver-major"],
    } in compose.get("ignore", [])
