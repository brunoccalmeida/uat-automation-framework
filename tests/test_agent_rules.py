"""Tests for the rules the AI agent (Claude Code) loads.

Every turn resends the always-loaded rules, so their size is paid in every
request of every chat, and a long file lowers adherence to each rule. The
official target is under 200 lines; rules that apply only to part of the code
live in path-scoped files, loaded only when the agent touches those paths.

The always-loaded rules live in ``AGENTS.md``, the open format for agent
instructions, imported by ``CLAUDE.md``; path-scoped rules live only in
``.claude/rules/`` (#173). A second copy for another agent would drift.
See docs/ai-workflow/AGENT_TOKEN_SPEND.md.
"""

import json
import re
import tomllib
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parent.parent
# CLAUDE.md @imports AGENTS.md: both load in every Claude chat
CLAUDE_MD = ROOT / "CLAUDE.md"
AGENTS_MD = ROOT / "AGENTS.md"
ALWAYS_LOADED = [CLAUDE_MD, AGENTS_MD]
MAX_ALWAYS_LOADED_LINES = 200
CLAUDE_RULES = ROOT / ".claude" / "rules"
# Copies of the rules in GitHub Copilot's format, removed in #173
COPILOT_COPIES = [
    ROOT / ".github" / "copilot-instructions.md",
    ROOT / ".github" / "instructions",
]
SKILLS = ROOT / ".claude" / "skills"
AGENTS = ROOT / ".claude" / "agents"
# Read at the start of every chat (#149). Both limits are a judgment call, not
# an official number: roughly a fifth of the 78 KB the file had reached, and a
# table row that fits one idea
SESSION_SUMMARY = ROOT / "docs" / "ai-workflow" / "PROJECT_SESSION_SUMMARY.md"
MAX_SESSION_SUMMARY_CHARS = 16_000
MAX_STATE_ROW_CHARS = 240
TESTS_WORKFLOW = ROOT / ".github" / "workflows" / "tests.yml"


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


class TestAlwaysLoadedRules:
    """The rules paid in every request stay under the official target."""

    def test_claude_md_imports_agents_md(self):
        # Claude Code reads AGENTS.md natively only from v2.1.277 and not in
        # every session; the import works in all of them (code.claude.com/docs/
        # en/memory, "Share one file with other coding tools", read 13/11/2026)
        lines = CLAUDE_MD.read_text(encoding="utf-8").splitlines()
        assert "@AGENTS.md" in lines

    @pytest.mark.parametrize("path", COPILOT_COPIES, ids=lambda path: path.name)
    def test_rules_have_a_single_copy(self, path):
        assert not path.exists()

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


class TestPathScopedRules:
    """Rules for part of the code load only when the agent touches it."""

    def test_path_scoped_rules_exist(self):
        assert _claude_names(), f"no path-scoped rules in {CLAUDE_RULES}"

    @pytest.mark.parametrize("name", sorted(_claude_names()))
    def test_rule_says_which_paths_it_applies_to(self, name):
        frontmatter, _ = _split_frontmatter(CLAUDE_RULES / f"{name}.md")
        assert frontmatter["paths"]


# Plugin that ships /mission:close-mission, /mission:ship-pr and the
# mission:reviewer agent (#179); its README defines the contracts
MARKETPLACE = "brunoccalmeida-plugins"
MISSION_PLUGIN = f"mission@{MARKETPLACE}"
# Local copies the plugin replaced (#179)
LOCAL_COPIES = [
    SKILLS / "close-mission",
    SKILLS / "ship-pr",
    AGENTS / "reviewer.md",
    ROOT / "scripts" / "wait_for_merge.py",
]
REQUIRED_CONTRACTS = {"check", "test", "main-branch", "gate", "session-summary"}
REVIEW_MD = ROOT / "REVIEW.md"


def _always_loaded_text():
    return "\n".join(path.read_text(encoding="utf-8") for path in ALWAYS_LOADED)


def _settings():
    return json.loads((ROOT / ".claude" / "settings.json").read_text("utf-8"))


class TestMissionPlugin:
    """The mission procedures come from one plugin, not from local copies.

    A local copy per project drifts; the plugin is the same in every project
    and is updated on purpose (``autoUpdate: false``), after reading what
    changed. ``extraKnownMarketplaces`` registers it for everyone who clones
    the repository (plugin README, "Install in a project").
    """

    def test_marketplace_is_registered_for_the_project(self):
        marketplace = _settings()["extraKnownMarketplaces"][MARKETPLACE]
        assert marketplace["source"] == {
            "source": "github",
            "repo": "brunoccalmeida/automation-template",
        }

    def test_plugin_updates_only_on_purpose(self):
        # the default is false today, but the install does not write it down
        marketplace = _settings()["extraKnownMarketplaces"][MARKETPLACE]
        assert marketplace["autoUpdate"] is False

    def test_plugin_is_enabled_for_the_project(self):
        assert _settings()["enabledPlugins"][MISSION_PLUGIN] is True

    @pytest.mark.parametrize("path", LOCAL_COPIES, ids=lambda path: path.name)
    def test_local_copy_is_gone(self, path):
        assert not path.exists()

    @pytest.mark.parametrize("skill", ["mission:ship-pr", "mission:close-mission"])
    def test_always_loaded_rules_point_to_the_plugin_skill(self, skill):
        assert f"`/{skill}`" in _always_loaded_text()

    @pytest.mark.parametrize("old", ["`/ship-pr", "`/close-mission"])
    def test_always_loaded_rules_drop_the_local_names(self, old):
        assert old not in _always_loaded_text()

    @pytest.mark.parametrize(
        "step", ["--match-head-commit", "gh run watch", "gh pr checks --watch"]
    )
    def test_merge_steps_stay_out_of_the_always_loaded_rules(self, step):
        # the plugin's ship-pr holds them; a copy here would be paid every turn
        assert step not in _always_loaded_text()


def _contracts():
    """Return the contract table of the always-loaded rules as {name: value}."""
    rows = [
        line.split("|")[1:3]
        for line in AGENTS_MD.read_text(encoding="utf-8").splitlines()
        if line.startswith("| `")
    ]
    return {name.strip().strip("`"): value.strip() for name, value in rows}


def _poetry_commands(contract):
    return re.findall(r"`(poetry run [^`]+)`", _contracts()[contract])


def _ci_text():
    return TESTS_WORKFLOW.read_text(encoding="utf-8")


class TestContracts:
    """The values behind the plugin's contracts match what CI really does.

    The plugin names contracts (``check``, ``test``, ``gate``...) and this
    project declares the real value of each in AGENTS.md. A value that drifts
    from tests.yml makes the local gates pass on something CI does not run.
    """

    def test_required_contracts_are_declared(self):
        assert REQUIRED_CONTRACTS <= set(_contracts())

    def test_main_branch_is_the_one_pull_requests_target(self):
        on = yaml.safe_load(_ci_text())[True]
        branch = _contracts()["main-branch"].strip("`")
        assert branch == "master"
        assert branch in on["pull_request"]["branches"]

    def test_gate_is_a_job_of_the_tests_workflow(self):
        gate = _contracts()["gate"].strip("`")
        assert gate == "ci-passed"
        assert gate in yaml.safe_load(_ci_text())["jobs"]

    def test_session_summary_path_exists(self):
        path = _contracts()["session-summary"].strip("`")
        assert (ROOT / path) == SESSION_SUMMARY

    @pytest.mark.parametrize("contract", ["check", "test", "smoke"])
    def test_commands_are_the_ones_ci_runs(self, contract):
        commands = _poetry_commands(contract)
        assert commands
        assert not [command for command in commands if command not in _ci_text()]

    def test_test_covers_every_ci_test_layer(self):
        commands = _poetry_commands("test")
        for layer in ["--ignore=tests/integration", "tests/integration/", "behave"]:
            assert any(layer in command for command in commands), layer

    def test_test_starts_the_grid_like_ci(self):
        # compose.yaml defaults to one session per node: without
        # SE_NODE_MAX_SESSIONS the -n auto workers queue for it (seen: the
        # integration layer took 4m55s locally)
        assert "SE_NODE_MAX_SESSIONS" in _contracts()["test"]
        assert "SELENIUM_REMOTE_URL" in _contracts()["test"]

    def test_test_sets_the_ci_environment(self):
        # Settings fails fast without them (seen in #179: a shell without
        # .env errors in tests/test_smoke.py); CI sets them in tests.yml env
        for name in yaml.safe_load(_ci_text())["env"]:
            assert name in _contracts()["test"], name


class TestReviewInstructions:
    """REVIEW.md holds this project's checks for mission:reviewer.

    The plugin's reviewer is generic; it reads REVIEW.md at the root for the
    project's own checks and for what to skip (plugin README, section 3).
    """

    def _text(self):
        return REVIEW_MD.read_text(encoding="utf-8")

    def test_review_checks_test_isolation(self):
        # Selenium docs, test_practices/encouraged: "Test independency" and
        # "Fresh browser per test"; no gate catches a test that relies on
        # state left by another, it only shows up as a flake under -n auto
        for term in ["before_scenario", "-n auto"]:
            assert term in self._text(), term

    @pytest.mark.parametrize("gate", ["black", "ruff", "pylint", "pyright"])
    def test_review_skips_what_the_static_gates_enforce(self, gate):
        skip = self._text().split("## Não reportar")[1]
        assert gate in skip

    def test_always_loaded_rules_point_to_it(self):
        assert "REVIEW.md" in _always_loaded_text()


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


# Each is a way to rerun a failed test until it passes
RETRY_PLUGINS = {"flaky", "pytest-rerunfailures", "pytest-retry"}
RETRY_SWITCHES = (
    "--reruns",
    "--retries",
    "--force-flaky",
    "nick-fields/retry",
    "wretry.action",
)
BEHAVE_AUTORETRY = "scenario_autoretry"


class TestFlakyTestPolicy:
    """A flaky test is recorded and fixed, never retried until green (#145).

    A retry turns the signal green and hides the cause (#129). The policy is
    in docs/FLAKY_TESTS.md; test_doc_links checks that the path exists.
    """

    def test_always_loaded_rules_point_to_the_policy(self):
        assert any(
            "docs/FLAKY_TESTS.md" in path.read_text("utf-8") for path in ALWAYS_LOADED
        )

    def test_no_retry_plugin_is_installed(self):
        packages = {package["name"] for package in _toml("poetry.lock")["package"]}
        assert not packages & RETRY_PLUGINS

    @pytest.mark.parametrize(
        "path",
        [
            ROOT / "pyproject.toml",
            *sorted((ROOT / ".github" / "workflows").glob("*.yml")),
        ],
        ids=lambda path: path.name,
    )
    def test_no_retry_switch_is_configured(self, path):
        text = path.read_text("utf-8")
        assert not [switch for switch in RETRY_SWITCHES if switch in text]

    def test_behave_scenarios_are_not_auto_retried(self):
        hooks = (ROOT / "features").rglob("*.py")
        assert not [p.name for p in hooks if BEHAVE_AUTORETRY in p.read_text("utf-8")]
