"""Tests for the lint gate: linters must be able to fail a commit and a PR.

A gate that never fails gives false confidence: excluded folders, pylint's
``--exit-zero`` and CI's ``continue-on-error`` hid real bugs (#27). CI runs
the same pre-commit hooks as the developer (one definition, dev/prod parity),
and the hooks call the linters through Poetry, so their versions come from
``poetry.lock`` instead of drifting in a second place.
"""

import json
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parent.parent
PRE_COMMIT = ROOT / ".pre-commit-config.yaml"
WORKFLOW = ROOT / ".github" / "workflows" / "tests.yml"
LINTERS = ("black", "flake8", "pylint", "pyright", "ruff")
VSCODE = ROOT / ".vscode"
RUN_HOOKS = "poetry run pre-commit run --all-files --show-diff-on-failure"


def _hooks():
    config = yaml.safe_load(PRE_COMMIT.read_text(encoding="utf-8"))
    return {hook["id"]: hook for repo in config["repos"] for hook in repo["hooks"]}


HOOKS = _hooks()
LINT_JOB = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))["jobs"]["lint"]


@pytest.mark.parametrize("linter", LINTERS)
class TestPreCommitLinters:
    """Each linter checks every file and fails the commit on a finding."""

    def test_linter_has_a_hook(self, linter):
        assert linter in HOOKS, f"{PRE_COMMIT.name} has no '{linter}' hook"

    def test_linter_checks_every_folder(self, linter):
        assert "exclude" not in HOOKS[linter]

    def test_linter_can_fail(self, linter):
        assert "--exit-zero" not in HOOKS[linter].get("args", [])

    def test_linter_version_comes_from_poetry_lock(self, linter):
        assert HOOKS[linter]["entry"].startswith(f"poetry run {linter}")


class TestCiLintJob:
    """CI runs the pre-commit hooks and fails the PR when one fails."""

    def test_job_runs_every_hook_on_every_file(self):
        commands = [step.get("run") for step in LINT_JOB["steps"]]
        assert RUN_HOOKS in commands

    def test_no_step_ignores_its_failure(self):
        ignored = [s["name"] for s in LINT_JOB["steps"] if s.get("continue-on-error")]
        assert not ignored, f"steps ignore failures: {ignored}"


class TestEditorSortsImportsLikeTheGate:
    """The editor sorts imports with ruff, the tool the gate runs (#28).

    VS Code's generic ``source.organizeImports`` asks every provider, Pylance
    included, whose order differs from ruff's: saving would undo the gate.
    """

    SETTINGS = json.loads((VSCODE / "settings.json").read_text(encoding="utf-8"))

    def test_ruff_extension_is_recommended(self):
        extensions = json.loads(
            (VSCODE / "extensions.json").read_text(encoding="utf-8")
        )
        assert "charliermarsh.ruff" in extensions["recommendations"]

    def test_save_sorts_imports_with_ruff_only(self):
        actions = self.SETTINGS["[python]"]["editor.codeActionsOnSave"]
        assert actions == {"source.organizeImports.ruff": "explicit"}
