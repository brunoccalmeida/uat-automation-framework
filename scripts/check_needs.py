#!/usr/bin/env python3
"""Fail unless every job the CI gate depends on succeeded.

Run by the ``ci-passed`` job with ``NEEDS: ${{ toJSON(needs) }}``, whose
shape is ``{"job-id": {"result": "success", "outputs": {}}, ...}``.

Allowlist: only an explicit "success" passes. "failure", "cancelled" and
"skipped" all fail, because a skipped job tested nothing. Runs on the
runner's system Python, so it uses the standard library only.

Exit code 0 = every job succeeded
Exit code 1 = some job did not succeed, or there was nothing to check
"""

import json
import os
import sys
from collections.abc import Mapping


def unsuccessful_jobs(needs: Mapping) -> list[str]:
    """Return "job: result" for each job whose result is not "success"."""
    return [
        f"{job}: {status.get('result')}"
        for job, status in needs.items()
        if status.get("result") != "success"
    ]


def main(environ: Mapping[str, str]) -> int:
    """Check the NEEDS variable and report the jobs that did not succeed."""
    needs = json.loads(environ.get("NEEDS") or "{}")
    if not needs:
        print("ERROR: no job results to check (NEEDS is empty)", file=sys.stderr)
        return 1

    failed = unsuccessful_jobs(needs)
    if failed:
        print("ERROR: required jobs did not succeed:", file=sys.stderr)
        print("\n".join(f"  {line}" for line in failed), file=sys.stderr)
        return 1

    print(f"OK: all {len(needs)} required jobs succeeded")
    return 0


if __name__ == "__main__":
    sys.exit(main(os.environ))
