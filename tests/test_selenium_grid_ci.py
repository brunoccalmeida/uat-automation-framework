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
- Dependabot watches compose.yaml, so the pinned digest does not go stale.
"""

import re
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parent.parent
COMPOSE = ROOT / "compose.yaml"
WORKFLOW = ROOT / ".github" / "workflows" / "tests.yml"
DEPENDABOT = ROOT / ".github" / "dependabot.yml"
BROWSERS = ("chrome", "firefox")
BROWSER_JOBS = ("smoke-matrix", "test")
PINNED_IMAGE = re.compile(
    r"^selenium/standalone-(?P<browser>chrome|firefox)"
    r":\d+\.\d+\.\d+-\d{8}@sha256:[0-9a-f]{64}$"
)
MATRIX_EXPRESSION = re.compile(r"\$\{\{\s*matrix\.(?P<key>[\w-]+)\s*\}\}")


def _load(path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


SERVICES = _load(COMPOSE)["services"]
JOBS = _load(WORKFLOW)["jobs"]


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
