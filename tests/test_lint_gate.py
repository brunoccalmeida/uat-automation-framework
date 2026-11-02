"""Tests for the lint gate: linters must be able to fail a commit and a PR.

A gate that never fails gives false confidence: excluded folders, pylint's
``--exit-zero`` and CI's ``continue-on-error`` hid real bugs (#27). CI runs
the same pre-commit hooks as the developer (one definition, dev/prod parity),
and the hooks call the linters through Poetry, so their versions come from
``poetry.lock`` instead of drifting in a second place.
"""

import json
import re
import subprocess
import sys
import tomllib
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parent.parent
PRE_COMMIT = ROOT / ".pre-commit-config.yaml"
WORKFLOW = ROOT / ".github" / "workflows" / "tests.yml"
PYPROJECT = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
LINTERS = ("black", "pylint", "pyright", "ruff")
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


class TestRuffReplacesFlake8:
    """ruff runs flake8's rules (#73): one tool, config in pyproject.toml.

    Two linters for the same rules mean two versions to update and a
    stand-alone ``.flake8``, which existed only because flake8 does not read
    ``pyproject.toml``.
    """

    def test_ruff_selects_the_flake8_rule_families(self):
        selected = PYPROJECT["tool"]["ruff"]["lint"]["select"]
        assert {"E", "W", "F"} <= set(selected)

    def test_flake8_is_gone(self):
        dev_deps = " ".join(PYPROJECT["dependency-groups"]["dev"])
        assert "flake8" not in HOOKS
        assert "flake8" not in dev_deps
        assert not (ROOT / ".flake8").exists()


def _linter_output(*args):
    # Same interpreter as this test run, so the linters come from the venv
    return subprocess.run(
        [sys.executable, "-m", *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    ).stdout


def _ruff_enabled_rules():
    """Names of the rules ruff runs, as ruff itself resolves the selectors."""
    settings = _linter_output("ruff", "check", "--show-settings", "pyproject.toml")
    enabled = settings.split("linter.rules.enabled = [", 1)[1].split("]", 1)[0]
    return set(re.findall(r"^\s*([a-z0-9-]+) \(", enabled, re.MULTILINE))


def _pylint_enabled_checks():
    listing = _linter_output("pylint", "--list-msgs-enabled")
    enabled = listing.split("Enabled messages:", 1)[1].split("Disabled messages:")[0]
    return set(re.findall(r"^\s+([a-z0-9-]+) \(", enabled, re.MULTILINE))


class TestRuffRunsPylintOverlap:
    """Each rule lives in one linter (#78), the Home Assistant pattern.

    ruff runs the pylint rules it implements (``PL``): it is the linter the
    editor shows while typing, with autofix. pylint keeps what needs its
    inference or exists only there (``duplicate-code``, ``abstract-method``),
    which the ruff FAQ says it does not replace. One rule in both would mean
    two reports and, for a deliberate exception, two suppressions.
    """

    def test_ruff_selects_the_pylint_rules(self):
        assert "PL" in PYPROJECT["tool"]["ruff"]["lint"]["select"]

    def test_ruff_ignores_magic_value_comparison(self):
        # In a test, the literal in an assert is the expected value under test
        assert "PLR2004" in PYPROJECT["tool"]["ruff"]["lint"]["ignore"]

    def test_no_pylint_check_also_runs_in_ruff(self):
        # Matched by name, a lower bound (SLF001 is protected-access): it
        # catches every overlap a ruff upgrade adds under pylint's own name.
        overlap = _pylint_enabled_checks() & _ruff_enabled_rules()
        assert not overlap, f"disable in [tool.pylint.main]: {sorted(overlap)}"


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
