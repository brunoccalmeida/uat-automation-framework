"""Claude Code PreToolUse hook: compact test-runner output.

Reads the hook payload on stdin and, for a ``pytest`` or ``behave`` command,
answers with the same command using the runner's compact output. Other
commands get ``{}`` (no change). See ``tests/test_filter_test_output.py``.
"""

import json
import re
import sys

# The runner must be the command itself, not an argument (``echo pytest``)
RUNNER = re.compile(r"^(?:poetry run\s+)?(pytest|behave)(?=\s|$)")
# behave pairs each -o with a -f in order, so an explicit formatter wins
BEHAVE_FORMAT = re.compile(r"(?:^|\s)(?:-f|--format)")
COMPACT_FLAGS = {"pytest": "-q", "behave": "-f progress2"}


def rewrite(command):
    """Return the command with compact output, or None to leave it as is."""
    match = RUNNER.match(command)
    if match is None:
        return None
    runner, end = match.group(1), match.end()
    rest = command[end:]
    if runner == "behave" and BEHAVE_FORMAT.search(rest):
        return None
    # Right after the runner, so the caller's own flags still take precedence
    return f"{command[:end]} {COMPACT_FLAGS[runner]}{rest}"


def main():
    """Run the hook: payload on stdin, decision on stdout."""
    tool_input = json.loads(sys.stdin.read())["tool_input"]
    rewritten = rewrite(tool_input.get("command", ""))
    if rewritten is None:
        print("{}")
    else:
        output = {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "updatedInput": {**tool_input, "command": rewritten},
            }
        }
        print(json.dumps(output))
    return 0


if __name__ == "__main__":
    sys.exit(main())
