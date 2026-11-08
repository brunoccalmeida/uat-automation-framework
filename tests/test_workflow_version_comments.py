"""Tests that every GitHub Action states its version in a trailing comment.

Pinning itself (a full commit SHA, because a tag is a movable pointer) is
enforced by zizmor in the ``workflow-audit`` job, which also catches a comment
that disagrees with the SHA. A *missing* comment is the one gap: zizmor reports
it only with the pedantic persona (docs, ``ref-version-mismatch``), whose other
findings do not apply here. Without the comment a SHA says nothing to whoever
reviews it, so this rule stays as a test (#147).
"""

import re
from pathlib import Path

import pytest

WORKFLOWS_DIR = Path(__file__).resolve().parent.parent / ".github" / "workflows"

USES_LINE = re.compile(r"^\s*(?:-\s*)?uses:\s*(?P<ref>\S+)(?P<rest>.*)$")
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
def test_action_states_its_version_in_a_comment(ref, rest):
    """Each action must be followed by a ``# vX.Y.Z`` comment."""
    assert VERSION_COMMENT.match(rest), f"{ref} lacks a '# vX.Y.Z' comment"
