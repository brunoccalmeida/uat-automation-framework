"""Every path the docs point to exists (#126).

Moving a doc (``docs/ai-workflow/``) must update every reference: README
links, rules, skills and the docs themselves. A broken link is found here,
not by a visitor. Only tracked files count (``git ls-files``), so local
personal notes neither add nor hide references.

Checked: relative Markdown links ``[text](path)`` (resolved from the file)
and code spans naming a repo path under ``docs/`` (resolved from the root,
the way rules and skills cite them).
"""

import re
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
MARKDOWN_LINK = re.compile(r"\]\((?P<target>[^)\s]+)\)")
DOCS_CODE_SPAN = re.compile(r"`(?P<path>docs/[\w./-]+)`")
EXTERNAL = ("http://", "https://", "mailto:", "#")


def _tracked_markdown():
    result = subprocess.run(
        ["git", "ls-files", "*.md"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return sorted(result.stdout.split())


def _broken_references(relative):
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


def test_markdown_files_are_found():
    assert "README.md" in _tracked_markdown()


@pytest.mark.parametrize("relative", _tracked_markdown())
def test_every_referenced_path_exists(relative):
    broken = _broken_references(relative)
    assert not broken
