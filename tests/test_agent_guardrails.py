"""The agent's guardrails: deny rules in .claude/settings.json (#146).

Deny rules match the command text, with ``*`` standing for any text
(Claude Code docs, Configure permissions → Wildcard patterns). They stop
the invocation the agent usually writes, not every spelling of it; the
server-side ruleset on master is the real boundary, these rules stop the
mistake before it gets there. ``_denied`` mirrors that documented
matching so the examples below pin what is blocked and, as important,
what is not (a rule too wide blocks everyday work and gets removed).
"""

import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SHELL_TOOLS = ("Bash", "PowerShell")


def _deny_rules():
    settings = json.loads((ROOT / ".claude" / "settings.json").read_text("utf-8"))
    return settings["permissions"]["deny"]


def _rule_matches(rule, tool, argument):
    match = re.fullmatch(r"(\w+)\((.*)\)", rule)
    if match is None or match[1] != tool:
        return False
    pattern = re.escape(match[2]).replace(r"\*", ".*")
    # A trailing " *" also matches the bare command, but only when it is
    # the rule's sole wildcard: "Bash(* --help *)" misses "npm --help"
    if match[2].count("*") == 1:
        pattern = re.sub(r"\\ \.\*$", r"(?: .*)?", pattern)
    return re.fullmatch(pattern, argument) is not None


def _denied(tool, argument):
    return any(_rule_matches(rule, tool, argument) for rule in _deny_rules())


BLOCKED_COMMANDS = [
    # Admin merge bypasses the master ruleset
    "gh pr merge 12 --admin",
    "gh pr merge --admin --squash 12",
    # Force pushes rewrite history
    "git push --force",
    "git push origin feature --force",
    "git push --force-with-lease origin feature",
    "git push -f",
    "git push -f origin feature",
    "git push origin feature -f",
    "git push origin -f feature",
    "git push origin +feature",
    # Direct pushes to master skip the pull request
    "git push origin master",
    "git push origin master --no-verify",
    "git push origin HEAD:master",
    "git push origin HEAD:master --no-verify",
    "git push -u origin feature:master",
    "git push origin refs/heads/master",
    "git push origin refs/heads/master --no-verify",
]

ALLOWED_COMMANDS = [
    "gh pr merge 12 --squash",
    "gh pr view 12",
    "git push",
    "git push -u origin security/146-agent-guardrails",
    "git push origin fix/fix-flaky-firefox",
    "git push origin feat/master-data",
    "git fetch origin master",
    "git pull origin master",
]


@pytest.mark.parametrize("tool", SHELL_TOOLS)
@pytest.mark.parametrize("command", BLOCKED_COMMANDS)
def test_dangerous_command_is_denied(tool, command):
    assert _denied(tool, command)


@pytest.mark.parametrize("tool", SHELL_TOOLS)
@pytest.mark.parametrize("command", ALLOWED_COMMANDS)
def test_everyday_command_is_not_denied(tool, command):
    assert not _denied(tool, command)


@pytest.mark.parametrize("tool", ["Read", "Edit"])
@pytest.mark.parametrize("path", [".env", ".env.local", "config/.env"])
def test_env_files_are_off_limits(tool, path):
    # Bare filenames match at any depth (gitignore semantics)
    prefix = f"{tool}("
    patterns = [r[len(prefix) : -1] for r in _deny_rules() if r.startswith(prefix)]
    assert any(Path(path).match(p) for p in patterns)


class TestMatcher:
    """The helper must read rules the way the docs describe."""

    def test_star_matches_any_text(self):
        assert _rule_matches("Bash(git push *--force*)", "Bash", "git push a --force")

    def test_trailing_star_matches_bare_command(self):
        assert _rule_matches("Bash(git log *)", "Bash", "git log")

    def test_trailing_star_matches_bare_command_only_as_sole_wildcard(self):
        # The docs' own example; probes in #146 confirmed it in both shells
        assert not _rule_matches("Bash(* --help *)", "Bash", "npm --help")

    def test_space_before_trailing_star_is_part_of_rule(self):
        assert not _rule_matches("Bash(ls *)", "Bash", "lsof")

    def test_rule_applies_only_to_its_tool(self):
        assert not _rule_matches("Bash(git push *)", "PowerShell", "git push")
