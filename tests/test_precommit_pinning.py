"""Tests that every remote pre-commit hook is pinned to immutable code.

A tag is a movable pointer: whoever controls the hook repository can point it
at other code, and every machine that installs the hooks afterwards runs it.
A full commit SHA cannot be moved, which is why the workflows pin actions the
same way (#140).

The ``# frozen: vX.Y.Z`` comment is the format ``pre-commit autoupdate --freeze``
writes, and it is more than documentation: per the Dependabot docs, a SHA with
no such comment is updated to the HEAD of the default branch instead of the
latest release. For the same reason the ``pre-commit`` ecosystem must stay in
``dependabot.yml``: a frozen hook with no updater silently stops receiving
fixes.

The cooldown of every ecosystem is checked here too: removing it from the
``pre-commit`` entry left zizmor 1.32.0 reporting no findings, so that audit
alone does not protect it.
"""

import re
from collections import Counter
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parent.parent
PRE_COMMIT = ROOT / ".pre-commit-config.yaml"
DEPENDABOT = ROOT / ".github" / "dependabot.yml"

REV_LINE = re.compile(r"^\s*rev:\s*(?P<rev>\S+)(?P<rest>.*)$")
FULL_SHA = re.compile(r"^[0-9a-f]{40}$")
FROZEN_COMMENT = re.compile(r"^\s*#\s*frozen:\s*v?\d+(\.\d+)*\s*$")
COOLDOWN_DAYS = 7


def _collect_revs():
    """Return (location, rev, rest-of-line) for each ``rev:`` of the config."""
    lines = PRE_COMMIT.read_text(encoding="utf-8").splitlines()
    return [
        (f"{PRE_COMMIT.name}:{number}", match["rev"], match["rest"])
        for number, match in enumerate(map(REV_LINE.match, lines), start=1)
        if match
    ]


def _remote_repos():
    """Return the URL of each remote repository, one item per entry."""
    config = yaml.safe_load(PRE_COMMIT.read_text(encoding="utf-8"))
    return [
        entry["repo"]
        for entry in config["repos"]
        if entry["repo"] not in ("local", "meta")
    ]


REVS = _collect_revs()
UPDATES = yaml.safe_load(DEPENDABOT.read_text(encoding="utf-8"))["updates"]


def pin_problem(rev, rest):
    """Return why this ``rev:`` breaks the pinning rule, or None if it complies."""
    if not FULL_SHA.match(rev):
        return f"'{rev}' is not a full commit SHA (a tag can be moved)"
    if not FROZEN_COMMENT.match(rest):
        return f"'{rev}' lacks a '# frozen: vX.Y.Z' comment"
    return None


def test_config_has_remote_hooks():
    """Guard against a vacuous pass (wrong path or parsing finds nothing)."""
    assert REVS, f"no 'rev:' found in {PRE_COMMIT}"
    assert _remote_repos(), f"no remote repository found in {PRE_COMMIT}"


@pytest.mark.parametrize(
    "rev,rest,expected",
    [
        ("a" * 40, "  # frozen: v5.0.0", None),
        ("a" * 40, "  # frozen: 5.0", None),
        ("v5.0.0", "", "not a full commit SHA"),
        ("v5.0.0", "  # frozen: v5.0.0", "not a full commit SHA"),
        ("a" * 39, "  # frozen: v5.0.0", "not a full commit SHA"),
        ("A" * 40, "  # frozen: v5.0.0", "not a full commit SHA"),
        ("a" * 40, "", "lacks a '# frozen"),
        ("a" * 40, "  # v5.0.0", "lacks a '# frozen"),
        ("a" * 40, "  # frozen: main", "lacks a '# frozen"),
    ],
    ids=[
        "valid",
        "valid-no-v-prefix",
        "tag",
        "tag-with-comment",
        "short-sha",
        "uppercase-sha",
        "no-comment",
        "comment-not-frozen",
        "frozen-branch",
    ],
)
def test_pin_problem(rev, rest, expected):
    """The rule itself, on synthetic values (including cases absent today)."""
    problem = pin_problem(rev, rest)
    if expected is None:
        assert problem is None
    else:
        assert problem is not None and expected in problem


@pytest.mark.parametrize(
    "rev,rest", [(rev, rest) for _, rev, rest in REVS], ids=[loc for loc, *_ in REVS]
)
def test_hook_is_pinned_by_frozen_sha(rev, rest):
    """Each remote hook must be pinned by SHA, with the tag in a comment."""
    problem = pin_problem(rev, rest)
    assert problem is None, problem


def test_each_remote_repository_appears_once():
    """Two entries for one repository can drift to different versions."""
    repeated = [url for url, count in Counter(_remote_repos()).items() if count > 1]
    assert not repeated, f"merge the repeated entries of: {repeated}"


def test_dependabot_updates_the_frozen_hooks():
    """A frozen hook with no updater silently stops receiving fixes."""
    ecosystems = [update["package-ecosystem"] for update in UPDATES]
    assert "pre-commit" in ecosystems, f"not in dependabot.yml: {ecosystems}"


@pytest.mark.parametrize(
    "update", UPDATES, ids=[update["package-ecosystem"] for update in UPDATES]
)
def test_every_ecosystem_waits_out_the_cooldown(update):
    """A compromised release is usually taken down within days, so wait."""
    days = update.get("cooldown", {}).get("default-days", 0)
    assert days >= COOLDOWN_DAYS, (
        f"{update['package-ecosystem']}: cooldown default-days is {days}, "
        f"expected at least {COOLDOWN_DAYS}"
    )
