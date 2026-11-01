"""Tests for the PreToolUse hook that keeps test-runner output short.

Every line a tool prints enters the agent's context and is resent on every
later turn. A passing ``behave`` run in the default pretty format prints every
step (~51 KB here); ``pytest -v`` prints every test (~28 KB). The hook rewrites
test commands to use the runners' own compact output (``pytest -q``, ``behave
-f progress2``), which still report every failure in full. (Plain
``progress`` lists failing scenarios but hides the assertion message.)

Native flags instead of the official example's ``| grep | head``: a pipe makes
the exit code that of the last command, so a failing run would look green.
"""

import io
import json
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

from scripts.filter_test_output import main, rewrite

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = "scripts/filter_test_output.py"


class TestHookRegistration:
    """A broken registration fails silently: the hook just stops running."""

    def _hooks(self):
        settings = json.loads((ROOT / ".claude" / "settings.json").read_text("utf-8"))
        return settings["hooks"]["PreToolUse"]

    def test_hook_covers_both_shell_tools(self):
        # On Windows Claude may route shell commands through PowerShell only
        (entry,) = [e for e in self._hooks() if SCRIPT in json.dumps(e)]
        assert set(entry["matcher"].split("|")) >= {"Bash", "PowerShell"}

    def test_hook_runs_the_script_in_exec_form(self):
        (entry,) = [e for e in self._hooks() if SCRIPT in json.dumps(e)]
        (hook,) = entry["hooks"]
        assert hook["command"] == "python"
        assert hook["args"] == [f"${{CLAUDE_PROJECT_DIR}}/{SCRIPT}"]
        assert (ROOT / SCRIPT).is_file()


class TestRewrite:
    """Test commands get compact output; everything else passes untouched."""

    @pytest.mark.parametrize(
        ("command", "expected"),
        [
            ("pytest", "pytest -q"),
            ("pytest tests/ -n auto", "pytest -q tests/ -n auto"),
            ("poetry run pytest tests/ -v", "poetry run pytest -q tests/ -v"),
            ("behave", "behave -f progress2"),
            (
                "poetry run behave --tags=@smoke",
                "poetry run behave -f progress2 --tags=@smoke",
            ),
        ],
    )
    def test_test_commands_get_compact_output(self, command, expected):
        assert rewrite(command) == expected

    @pytest.mark.parametrize(
        "command",
        [
            "behave -f allure_behave.formatter:AllureFormatter -o reports/allure",
            "behave --format=pretty",
            "poetry run behave --format pretty --tags=@e2e",
            "behave -fplain",
        ],
    )
    def test_behave_with_explicit_formatter_is_untouched(self, command):
        # behave pairs each -o with a -f in order: an extra -f would steal the -o
        assert rewrite(command) is None

    @pytest.mark.parametrize(
        "command",
        [
            "git status",
            "ls tests/",
            "pytesting",
            "poetry run behavex",
            "echo pytest",
            "grep -rn pytest .github/",
        ],
    )
    def test_other_commands_are_untouched(self, command):
        assert rewrite(command) is None


class TestHookProtocol:
    """The hook speaks Claude Code's PreToolUse JSON protocol on stdin/stdout."""

    def _run(self, monkeypatch, capsys, tool_input):
        payload = {"tool_name": "Bash", "tool_input": tool_input}
        monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps(payload)))
        assert main() == 0
        return json.loads(capsys.readouterr().out)

    def test_rewritten_command_keeps_the_other_input_fields(self, monkeypatch, capsys):
        # updatedInput replaces the whole input, so unchanged fields must be resent
        tool_input = {"command": "pytest", "description": "Run tests", "timeout": 60000}

        output = self._run(monkeypatch, capsys, tool_input)

        assert output == {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "updatedInput": {
                    "command": "pytest -q",
                    "description": "Run tests",
                    "timeout": 60000,
                },
            }
        }

    def test_other_commands_produce_no_changes(self, monkeypatch, capsys):
        assert self._run(monkeypatch, capsys, {"command": "git status"}) == {}


class TestFailuresStayVisible:
    """Compact output must still fail loudly: exit code and failure details."""

    def test_pytest_failure(self, tmp_path):
        (tmp_path / "test_broken.py").write_text(
            "def test_broken():\n    assert 1 == 2, 'deliberate failure'\n"
        )

        result = _run_rewritten("pytest test_broken.py -p no:cacheprovider", tmp_path)

        assert result.returncode == 1
        assert "deliberate failure" in result.stdout
        assert "1 failed" in result.stdout

    def test_behave_failure(self, tmp_path):
        steps = tmp_path / "features" / "steps"
        steps.mkdir(parents=True)
        (tmp_path / "features" / "broken.feature").write_text(textwrap.dedent("""\
                Feature: Broken
                  Scenario: Fails on purpose
                    Given a step that fails
                """))
        (steps / "broken_steps.py").write_text(textwrap.dedent("""\
                from behave import given

                @given("a step that fails")
                def step_fails(context):
                    assert False, "deliberate failure"
                """))

        result = _run_rewritten("behave", tmp_path)

        assert result.returncode != 0
        assert "deliberate failure" in result.stdout
        assert "Fails on purpose" in result.stdout


def _run_rewritten(command, cwd):
    rewritten = rewrite(command)
    assert rewritten is not None
    # Same interpreter as this test run, so the runners come from the venv
    runner, _, args = rewritten.partition(" ")
    return subprocess.run(
        f'"{sys.executable}" -m {runner} {args}',
        cwd=cwd,
        shell=True,
        capture_output=True,
        text=True,
        check=False,
    )
