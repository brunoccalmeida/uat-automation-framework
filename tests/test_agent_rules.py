"""Tests for the rules the AI agents (Claude Code, GitHub Copilot) load.

Every turn resends the always-loaded rules, so their size is paid in every
request of every chat, and a long file lowers adherence to each rule. The
official target is under 200 lines; rules that apply only to part of the code
live in path-scoped files, loaded only when the agent touches those paths.

Each tool reads path-scoped rules from its own directory and frontmatter
(Claude: ``.claude/rules/*.md`` with ``paths:``; Copilot:
``.github/instructions/*.instructions.md`` with ``applyTo``). The two copies
must stay identical, or one agent silently follows outdated rules.
See docs/AGENT_TOKEN_SPEND.md.
"""

from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parent.parent
# CLAUDE.md @imports the shared rules: both load in every Claude chat
ALWAYS_LOADED = [ROOT / "CLAUDE.md", ROOT / ".github" / "copilot-instructions.md"]
MAX_ALWAYS_LOADED_LINES = 200
CLAUDE_RULES = ROOT / ".claude" / "rules"
COPILOT_RULES = ROOT / ".github" / "instructions"
COPILOT_SUFFIX = ".instructions.md"


def _split_frontmatter(path):
    """Return (frontmatter dict, body) of a Markdown file with YAML frontmatter."""
    text = path.read_text(encoding="utf-8")
    _, frontmatter, body = text.split("---\n", 2)
    return yaml.safe_load(frontmatter), body


def _claude_names():
    return {path.stem for path in CLAUDE_RULES.glob("*.md")}


def _copilot_names():
    return {
        path.name.removesuffix(COPILOT_SUFFIX)
        for path in COPILOT_RULES.glob(f"*{COPILOT_SUFFIX}")
    }


class TestAlwaysLoadedRules:
    """The rules paid in every request stay under the official target."""

    def test_always_loaded_rules_are_under_the_line_target(self):
        lines = sum(
            len(path.read_text(encoding="utf-8").splitlines()) for path in ALWAYS_LOADED
        )
        assert lines < MAX_ALWAYS_LOADED_LINES, (
            f"always-loaded rules have {lines} lines; move rules that apply "
            "to part of the code to path-scoped files"
        )


class TestPathScopedRules:
    """Claude and Copilot load the same path-scoped rules for the same paths."""

    def test_path_scoped_rules_exist(self):
        assert _claude_names(), f"no path-scoped rules in {CLAUDE_RULES}"

    def test_every_rule_exists_for_both_agents(self):
        assert _claude_names() == _copilot_names()

    @pytest.mark.parametrize("name", sorted(_claude_names() & _copilot_names()))
    def test_rule_body_is_identical_for_both_agents(self, name):
        _, claude_body = _split_frontmatter(CLAUDE_RULES / f"{name}.md")
        _, copilot_body = _split_frontmatter(COPILOT_RULES / f"{name}{COPILOT_SUFFIX}")
        assert claude_body == copilot_body

    @pytest.mark.parametrize("name", sorted(_claude_names() & _copilot_names()))
    def test_rule_applies_to_the_same_paths_for_both_agents(self, name):
        claude, _ = _split_frontmatter(CLAUDE_RULES / f"{name}.md")
        copilot, _ = _split_frontmatter(COPILOT_RULES / f"{name}{COPILOT_SUFFIX}")
        copilot_globs = [glob.strip() for glob in copilot["applyTo"].split(",")]
        assert claude["paths"] == copilot_globs
