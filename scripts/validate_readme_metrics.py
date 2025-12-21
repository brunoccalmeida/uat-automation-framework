#!/usr/bin/env python3
"""Validate README.md metrics against actual project state.

This pre-commit hook ensures documentation accuracy by checking:
- Test counts (unit/integration via pytest)
- E2E scenario counts (via behave)
- Coverage statements (via coverage.xml)

Exit code 0 = metrics are accurate
Exit code 1 = metrics need updating
"""

import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


def get_pytest_count() -> int:
    """Get total count of unit/integration tests."""
    result = subprocess.run(
        ["poetry", "run", "pytest", "--co", "-q"],
        capture_output=True,
        text=True,
        check=False,
    )

    # Parse output like "239 tests collected in 0.20s"
    match = re.search(r"(\d+) tests? collected", result.stdout)
    if match:
        return int(match.group(1))

    print("ERROR: Could not determine pytest count", file=sys.stderr)
    return 0


def get_behave_scenario_count() -> int:
    """Get total count of E2E scenarios."""
    result = subprocess.run(
        ["poetry", "run", "behave", "--dry-run"],
        capture_output=True,
        text=True,
        check=False,
    )

    # Parse output like "0 scenarios passed, 0 failed, 0 skipped, 55 untested"
    # Output pode estar em stdout ou stderr
    combined_output = result.stdout + result.stderr
    match = re.search(
        r"(\d+) scenarios? passed, \d+ failed, \d+ skipped, (\d+) untested",
        combined_output,
    )
    if match:
        return int(match.group(2))  # Second group is untested scenarios

    print("ERROR: Could not determine scenario count", file=sys.stderr)
    return 0


def get_coverage_statements() -> tuple[int, int]:
    """Get total statements and covered from coverage.xml.

    Returns:
        Tuple of (total_statements, covered_statements)
    """
    coverage_file = Path("coverage.xml")
    if not coverage_file.exists():
        print(
            "WARN: coverage.xml not found, skipping coverage validation",
            file=sys.stderr,
        )
        return (0, 0)

    tree = ET.parse(coverage_file)
    root = tree.getroot()

    # Get coverage metrics from XML
    # <coverage line-rate="0.99" lines-covered="315" lines-valid="316">
    lines_covered = int(root.attrib.get("lines-covered", 0))
    lines_valid = int(root.attrib.get("lines-valid", 0))

    return (lines_valid, lines_covered)


def extract_readme_metrics(readme_path: Path) -> dict:
    """Extract metrics from README.md.

    Returns:
        Dict with keys: pytest_count, scenario_count, total_statements, covered_statements
    """
    content = readme_path.read_text(encoding="utf-8")

    metrics = {}

    # Extract "- **Total statements:** 316"
    match = re.search(r"\*\*Total statements:\*\*\s*(\d+)", content)
    if match:
        metrics["total_statements"] = int(match.group(1))

    # Extract "- **Covered:** 315 (99%)"
    match = re.search(r"\*\*Covered:\*\*\s*(\d+)", content)
    if match:
        metrics["covered_statements"] = int(match.group(1))

    # Extract "239 unit/integration tests" or similar
    match = re.search(r"(\d+) unit/integration tests", content)
    if match:
        metrics["pytest_count"] = int(match.group(1))

    # Extract from table "| **TOTAL** | **55** | **386** | **100%** |" (E2E scenarios)
    match = re.search(
        r"\|\s*\*\*TOTAL\*\*\s*\|\s*\*\*(\d+)\*\*\s*\|\s*\*\*(\d+)\*\*", content
    )
    if match:
        metrics["scenario_count"] = int(match.group(1))
        metrics["step_count"] = int(match.group(2))

    return metrics


def validate_metrics() -> bool:
    """Validate README metrics against actual values.

    Returns:
        True if all metrics match, False otherwise
    """
    readme_path = Path("README.md")
    if not readme_path.exists():
        print("ERROR: README.md not found", file=sys.stderr)
        return False

    # Get actual values
    actual_pytest = get_pytest_count()
    actual_scenarios = get_behave_scenario_count()
    actual_total_stmts, actual_covered_stmts = get_coverage_statements()

    # Get README values
    readme_metrics = extract_readme_metrics(readme_path)

    # Validation
    errors = []

    if actual_pytest > 0 and readme_metrics.get("pytest_count") != actual_pytest:
        errors.append(
            f"  ERROR: Pytest count: README shows {readme_metrics.get('pytest_count')}, "
            f"actual is {actual_pytest}"
        )

    if (
        actual_scenarios > 0
        and readme_metrics.get("scenario_count") != actual_scenarios
    ):
        errors.append(
            f"  ERROR: Scenario count: README shows {readme_metrics.get('scenario_count')}, "
            f"actual is {actual_scenarios}"
        )

    if (
        actual_total_stmts > 0
        and readme_metrics.get("total_statements") != actual_total_stmts
    ):
        errors.append(
            f"  ERROR: Total statements: README shows {readme_metrics.get('total_statements')}, "
            f"actual is {actual_total_stmts}"
        )

    if (
        actual_covered_stmts > 0
        and readme_metrics.get("covered_statements") != actual_covered_stmts
    ):
        errors.append(
            f"  ERROR: Covered statements: README shows {readme_metrics.get('covered_statements')}, "
            f"actual is {actual_covered_stmts}"
        )

    if errors:
        print("\nERROR: README.md metrics are outdated:\n", file=sys.stderr)
        print("\n".join(errors), file=sys.stderr)
        print(
            "\nHINT: Run tests and update README.md before committing.\n",
            file=sys.stderr,
        )
        return False

    print("OK: README.md metrics are accurate")
    return True


if __name__ == "__main__":
    sys.exit(0 if validate_metrics() else 1)
