"""Tests for the rules the AI agents (Claude Code, GitHub Copilot) load.

Every turn resends the always-loaded rules, so their size is paid in every
request of every chat, and a long file lowers adherence to each rule. The
official target is under 200 lines; rules that apply only to part of the code
live in path-scoped files, loaded only when the agent touches those paths.

Each tool reads path-scoped rules from its own directory and frontmatter
(Claude: ``.claude/rules/*.md`` with ``paths:``; Copilot:
``.github/instructions/*.instructions.md`` with ``applyTo``). The two copies
must stay identical, or one agent silently follows outdated rules.
See docs/ai-workflow/AGENT_TOKEN_SPEND.md.
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
# Copilot in VS Code reads skills and agents from these same folders, with the
# same disable-model-invocation field, so there is one copy (VS Code docs:
# copilot/customization/agent-skills and custom-agents, read 02/11/2026)
SKILLS = ROOT / ".claude" / "skills"
AGENTS = ROOT / ".claude" / "agents"
# Read at the start of every chat (#149). Both limits are a judgment call, not
# an official number: roughly a fifth of the 78 KB the file had reached, and a
# table row that fits one idea
SESSION_SUMMARY = ROOT / "docs" / "ai-workflow" / "PROJECT_SESSION_SUMMARY.md"
MAX_SESSION_SUMMARY_CHARS = 16_000
MAX_STATE_ROW_CHARS = 240


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


def _session_summary():
    return SESSION_SUMMARY.read_text(encoding="utf-8")


def _state_table_rows():
    section = _session_summary().split("## Estado atual")[1].split("\n## ")[0]
    return [line for line in section.splitlines() if line.startswith("|")]


class TestSessionSummary:
    """The handoff holds state: what is true now, not how it came to be.

    Every chat pays for this file, and history already has a home (issues, PR
    bodies, Git). It reached 78 KB because close-mission asked for a history
    paragraph per mission, so the procedure is checked along with the file.
    """

    def test_session_summary_stays_short(self):
        chars = len(_session_summary())
        assert chars <= MAX_SESSION_SUMMARY_CHARS, (
            f"session summary has {chars} characters; history belongs in the "
            "PR body, lasting decisions in the rules"
        )

    def test_session_summary_has_no_mission_history_paragraphs(self):
        history = [
            line[:40]
            for line in _session_summary().splitlines()
            if line.startswith("Do #")
        ]
        assert not history

    def test_state_table_exists(self):
        assert _state_table_rows()

    def test_state_table_rows_hold_state_only(self):
        long_rows = [
            row[:40] for row in _state_table_rows() if len(row) > MAX_STATE_ROW_CHARS
        ]
        assert not long_rows

    def test_close_mission_sends_history_to_the_pr_body(self):
        _, body = _split_frontmatter(SKILLS / "close-mission" / "SKILL.md")
        assert "corpo do PR" in body
        assert 'parágrafo "Do #N"' not in body


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


def _skills():
    return {path.parent.name: path for path in SKILLS.glob("*/SKILL.md")}


def _always_loaded_text():
    return "\n".join(path.read_text(encoding="utf-8") for path in ALWAYS_LOADED)


class TestSkills:
    """Procedures live in skills, whose body loads only when the skill is used.

    A procedure in the always-loaded rules is paid in every turn of every
    chat; a copy in both places drifts. A skill with side effects outside the
    repository (a merge to master publishes the report) is started only by the
    user (``disable-model-invocation``); the others stay available to the
    agent, because the mission cycle runs without being asked.
    """

    USER_ONLY = {"ship-pr"}

    def test_expected_skills_exist(self):
        assert {"ship-pr", "close-mission"} <= set(_skills())

    @pytest.mark.parametrize("name", sorted(_skills()))
    def test_skill_name_matches_its_directory(self, name):
        frontmatter, _ = _split_frontmatter(_skills()[name])
        assert frontmatter["name"] == name

    @pytest.mark.parametrize("name", sorted(_skills()))
    def test_skill_says_when_to_use_it(self, name):
        frontmatter, _ = _split_frontmatter(_skills()[name])
        assert frontmatter["description"].strip()

    @pytest.mark.parametrize("name", sorted(_skills()))
    def test_only_skills_with_side_effects_are_user_only(self, name):
        frontmatter, _ = _split_frontmatter(_skills()[name])
        user_only = frontmatter.get("disable-model-invocation", False)
        assert user_only is (name in self.USER_ONLY)

    @pytest.mark.parametrize("name", ["ship-pr", "close-mission"])
    def test_always_loaded_rules_point_to_the_skill(self, name):
        assert f"`/{name}`" in _always_loaded_text()

    @pytest.mark.parametrize(
        "name, procedure",
        [
            ("ship-pr", "scripts/wait_for_merge.py"),
            # the session record rides in the mission PR (#126)
            ("close-mission", "nunca abra PR separado de registro"),
        ],
    )
    def test_procedure_lives_only_in_its_skill(self, name, procedure):
        _, body = _split_frontmatter(SKILLS / name / "SKILL.md")
        assert procedure in body
        assert procedure not in _always_loaded_text()

    @pytest.mark.parametrize(
        "step", ["--match-head-commit", "gh run watch", "gh pr checks --watch"]
    )
    def test_merge_steps_left_the_always_loaded_rules(self, step):
        # the /ship-pr skill holds them; scripts/wait_for_merge.py says why
        assert step not in _always_loaded_text()

    def test_ship_pr_enables_native_auto_merge_bound_to_the_head(self):
        _, body = _split_frontmatter(SKILLS / "ship-pr" / "SKILL.md")
        assert "gh pr merge <n> --auto --squash --match-head-commit <sha>" in body

    def test_ship_pr_cleans_up_only_after_confirming_merged(self):
        _, body = _split_frontmatter(SKILLS / "ship-pr" / "SKILL.md")
        confirm = body.index("confirme `MERGED`")
        assert confirm < body.index("git pull --ff-only")

    def test_ship_pr_reads_live_state_when_a_wait_stops(self):
        _, body = _split_frontmatter(SKILLS / "ship-pr" / "SKILL.md")
        assert "estado real" in body


class TestReviewerSubagent:
    """A reviewer that hasn't seen how the code was written and can't edit it.

    The read-only limit is enforced by Claude Code from ``tools``, not asked
    for in the prompt. ``inherit`` keeps the session model: review quality is
    the reason this subagent exists, and without it an alias or the
    ``CLAUDE_CODE_SUBAGENT_MODEL`` variable could pick a smaller one.
    """

    def _frontmatter(self):
        frontmatter, _ = _split_frontmatter(AGENTS / "reviewer.md")
        return frontmatter

    def test_reviewer_says_when_to_use_it(self):
        frontmatter = self._frontmatter()
        assert frontmatter["name"] == "reviewer"
        assert frontmatter["description"].strip()

    def test_reviewer_can_only_read(self):
        tools = {tool.strip() for tool in self._frontmatter()["tools"].split(",")}
        assert tools == {"Read", "Grep", "Glob"}

    def test_reviewer_runs_on_the_session_model(self):
        assert self._frontmatter()["model"] == "inherit"


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
    See docs/ai-workflow/AGENT_TOKEN_SPEND.md.
    """

    def test_plugin_is_enabled_for_the_project(self):
        settings = json.loads((ROOT / ".claude" / "settings.json").read_text("utf-8"))
        assert settings["enabledPlugins"]["pyright-lsp@claude-plugins-official"]

    def test_pyright_uses_the_project_virtualenv(self):
        pyright = _toml("pyproject.toml")["tool"]["pyright"]
        assert (pyright["venvPath"], pyright["venv"]) == (".", ".venv")

    def test_poetry_creates_the_virtualenv_in_project(self):
        assert _toml("poetry.toml")["virtualenvs"]["in-project"] is True
