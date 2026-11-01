"""Tests that every GitHub Action is pinned to a full commit SHA.

A tag (``@v1``) is a movable pointer: whoever controls the action's repository
can retarget it, and the workflow then runs that code with the job's secrets.
A full commit SHA is immutable. The trailing ``# vX.Y.Z`` comment keeps the
version readable and lets Dependabot update the SHA and comment together.
"""

import re
from pathlib import Path

import pytest

WORKFLOWS_DIR = Path(__file__).resolve().parent.parent / ".github" / "workflows"

USES_LINE = re.compile(r"^\s*(?:-\s*)?uses:\s*(?P<ref>\S+)(?P<rest>.*)$")
PINNED_REF = re.compile(r"^[\w.-]+/[\w./-]+@[0-9a-f]{40}$")
VERSION_COMMENT = re.compile(r"^\s*#\s*v\d+(\.\d+)*\s*$")


def _collect_uses():
    """Return (location, ref, rest-of-line) for each remote ``uses:``."""
    found = []
    for workflow in sorted(WORKFLOWS_DIR.glob("*.y*ml")):
        lines = workflow.read_text(encoding="utf-8").splitlines()
        for number, line in enumerate(lines, start=1):
            match = USES_LINE.match(line)
            if match and not match["ref"].startswith("./"):
                location = f"{workflow.name}:{number}"
                found.append((location, match["ref"], match["rest"]))
    return found


USES = _collect_uses()


def test_workflows_reference_actions():
    """Guard against a vacuous pass (wrong path or parsing finds nothing)."""
    assert USES, f"no 'uses:' found under {WORKFLOWS_DIR}"


@pytest.mark.parametrize(
    "ref,rest", [(ref, rest) for _, ref, rest in USES], ids=[loc for loc, *_ in USES]
)
def test_action_is_pinned_to_full_commit_sha(ref, rest):
    """Each action must use a 40-char SHA followed by a version comment."""
    assert PINNED_REF.match(ref), f"{ref} is not pinned to a full commit SHA"
    assert VERSION_COMMENT.match(rest), f"{ref} lacks a '# vX.Y.Z' comment"
