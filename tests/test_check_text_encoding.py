"""Tests for the text encoding gate: every text file must be UTF-8 (#26).

Windows PowerShell 5.1 ``echo >>`` appends UTF-16, so ``.gitignore`` ended
with ``d\\0e\\0b\\0u\\0g\\0...``: Git matched nothing and ``debug_*.py`` files
showed up as untracked. NUL is valid UTF-8 (U+0000), so decoding alone would
accept that file; the gate also rejects NUL bytes.
"""

import subprocess
from pathlib import Path

import pytest
import yaml

from scripts.check_text_encoding import encoding_problem, main

ROOT = Path(__file__).resolve().parent.parent
PRE_COMMIT = ROOT / ".pre-commit-config.yaml"


def _hooks():
    config = yaml.safe_load(PRE_COMMIT.read_text(encoding="utf-8"))
    return {hook["id"]: hook for repo in config["repos"] for hook in repo["hooks"]}


class TestEncodingProblem:
    """UTF-8 without NUL passes; anything else is reported."""

    @pytest.mark.parametrize(
        "data",
        [b"", b"debug_*.py\r\n", "Ação, não é?\n".encode("utf-8")],
    )
    def test_utf8_text_passes(self, data):
        assert encoding_problem(data) is None

    def test_nul_byte_is_reported(self):
        # ASCII as UTF-16-LE without BOM: valid UTF-8, but full of NULs.
        problem = encoding_problem("debug_*.py\n".encode("utf-16-le"))
        assert problem is not None and "NUL" in problem

    @pytest.mark.parametrize("encoding", ["utf-16", "latin-1"])
    def test_non_utf8_text_is_reported(self, encoding):
        problem = encoding_problem("Ação\n".encode(encoding))
        assert problem is not None and "UTF-8" in problem


class TestMain:
    """The hook exits 1 and names each bad file, so the commit fails."""

    def test_utf8_files_pass(self, tmp_path, capsys):
        good = tmp_path / "good.txt"
        good.write_bytes("ok\n".encode("utf-8"))
        assert main([str(good)]) == 0
        assert capsys.readouterr().err == ""

    def test_bad_file_fails_and_is_named(self, tmp_path, capsys):
        good = tmp_path / "good.txt"
        good.write_bytes(b"ok\n")
        bad = tmp_path / "bad.txt"
        bad.write_bytes("ok\n".encode("utf-16"))
        assert main([str(good), str(bad)]) == 1
        err = capsys.readouterr().err
        assert str(bad) in err and str(good) not in err


class TestPreCommitHook:
    """The gate runs on every text file at commit time and in CI."""

    def test_hook_exists(self):
        assert "check-text-encoding" in _hooks()

    def test_hook_checks_text_files_everywhere(self):
        # identify tags known names (.gitignore, .txt, .md) as text by name,
        # without reading the content, so UTF-16 files still reach the hook.
        hook = _hooks()["check-text-encoding"]
        assert hook["types"] == ["text"]
        assert "exclude" not in hook


def test_line_endings_do_not_depend_on_local_config():
    """``* text=auto``: Git stores LF whatever each clone's ``core.autocrlf``."""
    result = subprocess.run(
        ["git", "check-attr", "text", "--", "any.txt"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.stdout.strip().endswith("text: auto")


def test_gitignore_rules_apply():
    """Regression for #26: the UTF-16 tail made Git skip ``debug_*.py``."""
    result = subprocess.run(
        ["git", "check-ignore", "--quiet", "debug_probe.py"],
        cwd=ROOT,
        check=False,
    )
    assert result.returncode == 0, ".gitignore does not ignore debug_*.py"
