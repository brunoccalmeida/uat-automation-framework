#!/usr/bin/env python3
"""Fail if a text file is not UTF-8 (#26).

Windows PowerShell 5.1 ``echo >>`` appends UTF-16, and Git then reads the
file byte by byte: a UTF-16 ``.gitignore`` line matches nothing, silently.
NUL is valid UTF-8 (U+0000) but never appears in this repo's text, so it is
rejected too: ASCII as UTF-16 without BOM would otherwise decode cleanly.

Run by pre-commit with ``types: [text]``. identify tags known names
(``.gitignore``, ``.md``, ``.txt``...) as text by name, without reading the
content, so UTF-16 files still reach this hook. Known gap: a file with an
unknown extension is tagged by content, and UTF-16 there counts as binary.

Exit code 0 = every file is UTF-8 without NUL
Exit code 1 = some file is not
"""

import sys
from collections.abc import Sequence
from pathlib import Path


def encoding_problem(data: bytes) -> str | None:
    """Return why ``data`` is not UTF-8 text, or None if it is."""
    try:
        data.decode("utf-8")
    except UnicodeDecodeError as error:
        return f"not UTF-8 (byte {error.start})"
    if b"\0" in data:
        return f"NUL byte at {data.index(b'\0')} (UTF-16?)"
    return None


def main(paths: Sequence[str]) -> int:
    """Check each file and report the ones that are not UTF-8."""
    problems = {
        path: problem
        for path in paths
        if (problem := encoding_problem(Path(path).read_bytes())) is not None
    }
    for path, problem in problems.items():
        print(f"{path}: {problem}; save it as UTF-8", file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
