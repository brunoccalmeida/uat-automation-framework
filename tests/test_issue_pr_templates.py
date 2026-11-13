"""Tests for the issue forms and the pull request template (#148).

Mission issues followed the shape Observed / Acceptance criteria by habit only.
An issue form makes GitHub refuse to submit without the required fields, and the
PR template asks for the evidence the TDD rule demands (how RED was seen).

Whether each file is a valid form is the job of the ``check-jsonschema`` hooks
(SchemaStore schemas, the same ones GitHub's format is published in). An invalid
form is not reported when the issue is opened: it just disappears from the
template chooser. These tests cover what the schema cannot know: which fields
this project requires, and that the gate validating them stays wired.
"""

from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parent.parent
ISSUE_TEMPLATES = ROOT / ".github" / "ISSUE_TEMPLATE"
PR_TEMPLATE = ROOT / ".github" / "pull_request_template.md"
PRE_COMMIT = ROOT / ".pre-commit-config.yaml"
CLOSE_MISSION = ROOT / ".claude" / "skills" / "close-mission" / "SKILL.md"

REQUIRED_FIELDS = {
    "1-mission.yml": {"observed", "acceptance-criteria"},
    "2-bug.yml": {"what-happened", "expected", "steps"},
}


def _load(path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _fields(form):
    """Map id -> element for every non-markdown element of a form."""
    return {item["id"]: item for item in form["body"] if item["type"] != "markdown"}


@pytest.mark.parametrize("filename", sorted(REQUIRED_FIELDS))
def test_form_requires_the_fields_the_project_depends_on(filename):
    """A required field is the only way GitHub refuses an incomplete issue."""
    fields = _fields(_load(ISSUE_TEMPLATES / filename))
    for field_id in REQUIRED_FIELDS[filename]:
        assert fields[field_id]["validations"]["required"] is True, field_id


def test_blank_issues_are_disabled():
    """With blank issues on, a contributor can skip the forms entirely."""
    assert _load(ISSUE_TEMPLATES / "config.yml")["blank_issues_enabled"] is False


@pytest.mark.parametrize(
    "expected",
    ["Closes #", "## How RED was seen"],
)
def test_pr_template_asks_for_the_issue_and_the_red_evidence(expected):
    """`Closes #` closes the issue on merge; a never-failed test proves nothing."""
    assert expected in PR_TEMPLATE.read_text(encoding="utf-8")


@pytest.mark.parametrize(
    "hook_id", ["check-github-issue-forms", "check-github-issue-config"]
)
def test_issue_templates_are_validated_by_pre_commit(hook_id):
    """An invalid form vanishes from the chooser silently; the schema catches it."""
    hook_ids = {
        hook["id"] for repo in _load(PRE_COMMIT)["repos"] for hook in repo["hooks"]
    }
    assert hook_id in hook_ids


def test_close_mission_points_the_pr_body_to_the_template():
    """`gh pr create --body` skips the template, so the agent must follow it by hand."""
    assert ".github/pull_request_template.md" in CLOSE_MISSION.read_text(
        encoding="utf-8"
    )
