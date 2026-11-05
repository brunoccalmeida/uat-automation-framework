"""Every path the docs point to exists (#126).

Moving a doc (``docs/ai-workflow/``) must update every reference: README
links, rules, skills, test docstrings and the docs themselves. A broken
link is found here, not by a visitor. Only tracked files count
(``git ls-files``), so local personal notes neither add nor hide references.

Checked in Markdown: relative links ``[text](path)`` (resolved from the
file) and code spans naming a repo path under ``docs/`` (resolved from the
root, the way rules and skills cite them). Checked in Python: file paths
under ``docs/`` (docstrings and comments cite them without backticks).
"""

import re
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
MARKDOWN_LINK = re.compile(r"\]\((?P<target>[^)\s]+)\)")
DOCS_CODE_SPAN = re.compile(r"`(?P<path>docs/[\w./-]+)`")
DOCS_FILE = re.compile(r"(?P<path>docs/[\w./-]+\.\w+)")
EXTERNAL = ("http://", "https://", "mailto:", "#")


def _tracked(pattern):
    result = subprocess.run(
        ["git", "ls-files", pattern],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return sorted(result.stdout.split())


def _broken_markdown_references(relative):
    path = ROOT / relative
    text = path.read_text(encoding="utf-8")
    broken = []
    for match in MARKDOWN_LINK.finditer(text):
        target = match["target"]
        if target.startswith(EXTERNAL):
            continue
        if not (path.parent / target.split("#")[0]).exists():
            broken.append(target)
    for match in DOCS_CODE_SPAN.finditer(text):
        if not (ROOT / match["path"]).exists():
            broken.append(match["path"])
    return broken


def _broken_python_references(relative):
    text = (ROOT / relative).read_text(encoding="utf-8")
    return [
        match["path"]
        for match in DOCS_FILE.finditer(text)
        if not (ROOT / match["path"]).exists()
    ]


def test_files_are_found():
    assert "README.md" in _tracked("*.md")
    assert "tests/test_agent_rules.py" in _tracked("*.py")


@pytest.mark.parametrize("relative", _tracked("*.md"))
def test_every_path_cited_in_markdown_exists(relative):
    broken = _broken_markdown_references(relative)
    assert not broken


@pytest.mark.parametrize("relative", _tracked("*.py"))
def test_every_docs_path_cited_in_python_exists(relative):
    broken = _broken_python_references(relative)
    assert not broken
