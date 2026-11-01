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

import json
import tomllib
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


def _vscode(name):
    """Return a shared VS Code workspace file (.vscode/<name>.json) as a dict."""
    return json.loads((ROOT / ".vscode" / f"{name}.json").read_text("utf-8"))


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

    def test_copilot_applies_path_scoped_rules_in_vscode(self):
        # VS Code attaches applyTo rules only with this setting on; its default
        # is undocumented, so the workspace states it
        assert _vscode("settings")["chat.includeApplyingInstructions"] is True


class TestEditorDiagnostics:
    """The editor attaches its diagnostics to the agent context after each edit.

    LTeX+ spelling flags every English technical term in pt-BR/es docs (39 of
    45 diagnostics on one doc in #52); spelling is left to Code Spell Checker,
    which knows English terms and project words, and LTeX+ keeps its grammar
    rules. Turning one spell checker off is only safe if the other one checks
    every language the docs are written in.
    """

    @pytest.mark.parametrize(
        "language, rule",
        [("pt-BR", "MORFOLOGIK_RULE_PT_BR"), ("es", "MORFOLOGIK_RULE_ES")],
    )
    def test_ltex_spelling_rule_is_disabled(self, language, rule):
        assert rule in _vscode("settings")["ltex.disabledRules"][language]

    @pytest.mark.parametrize("language", ["en", "pt_BR", "es"])
    def test_spell_checker_checks_every_doc_language(self, language):
        languages = _vscode("settings")["cSpell.language"].split(",")
        assert language in languages

    @pytest.mark.parametrize("word", ["claude", "ltex", "remov", "deprecat"])
    def test_project_word_is_known_to_the_spell_checker(self, word):
        assert word in _vscode("settings")["cSpell.words"]

    @pytest.mark.parametrize(
        "extension",
        [
            "ltex-plus.vscode-ltex-plus",
            "streetsidesoftware.code-spell-checker",
            "streetsidesoftware.code-spell-checker-portuguese-brazilian",
            "streetsidesoftware.code-spell-checker-spanish",
        ],
    )
    def test_checker_extension_is_recommended(self, extension):
        assert extension in _vscode("extensions")["recommendations"]


def _toml(name):
    """Return a TOML file at the repository root as a dict."""
    return tomllib.loads((ROOT / name).read_text("utf-8"))


class TestCodeIntelligence:
    """The pyright-lsp plugin reports type errors to the agent after each edit.

    Claude Code spawns ``pyright-langserver`` by name from PATH, so the server
    is a per-machine tool (``pipx install "pyright[nodejs]"``), not a Poetry
    dependency. Installed outside the project, pyright only resolves the
    project's imports (selenium, behave) if pointed at its virtualenv, and that
    path only exists for every collaborator if Poetry creates it in-project.
    See docs/AGENT_TOKEN_SPEND.md.
    """

    def test_plugin_is_enabled_for_the_project(self):
        settings = json.loads((ROOT / ".claude" / "settings.json").read_text("utf-8"))
        assert settings["enabledPlugins"]["pyright-lsp@claude-plugins-official"]

    def test_pyright_uses_the_project_virtualenv(self):
        pyright = _toml("pyproject.toml")["tool"]["pyright"]
        assert (pyright["venvPath"], pyright["venv"]) == (".", ".venv")

    def test_poetry_creates_the_virtualenv_in_project(self):
        assert _toml("poetry.toml")["virtualenvs"]["in-project"] is True
