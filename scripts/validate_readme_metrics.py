#!/usr/bin/env python3
"""Keep the README metrics in sync with the actual project state.

A pre-commit hook in the style of black: it rewrites what it can derive and
fails when it changed something, so the fix shows up as a diff to review.

- Test tables: every row names its test files in a Source column; the hook
  rewrites the Tests/Scenarios/Steps of each row and of the TOTAL row from
  `pytest --co` and `behave --dry-run`. A file in no row, or in two, fails.
- Layer summary: the unit/integration/E2E totals.
- Coverage statements (from coverage.xml): only checked, skipped without it.
- Translations (#39): the same rewrite, with each language's labels. Each one
  records the fingerprint of the README.md it was translated from (as MDN's
  l10n.sourceCommit) and fails once README.md changes after it.

Exit code 0 = metrics are accurate and the translations are current
Exit code 1 = a README was updated, or something needs a human fix
"""

import hashlib
import json
import re
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

# The CI runs the unit and integration layers apart by this folder
# (.github/workflows/tests.yml); the summary splits the counts the same way.
INTEGRATION_DIR = "tests/integration/"

README = "README.md"


@dataclass(frozen=True)
class Locale:
    """The words a README uses for what the hook reads and writes.

    columns maps each metric column header to its English name. In summary,
    "{n}" marks each number the hook rewrites, in the order of the values.
    """

    source: str
    columns: dict[str, str]
    summary: tuple[tuple[str, str], ...]
    statements: str
    covered: str


EN = Locale(
    source="Source",
    columns={"Tests": "Tests", "Scenarios": "Scenarios", "Steps": "Steps"},
    summary=(
        ("Unit Tests", "**Unit Tests**: {n} tests"),
        ("Integration Tests", "**Integration Tests**: {n} tests"),
        ("E2E Tests", "**E2E Tests**: {n} scenarios, {n} steps"),
        ("Total", "**Total**: {n} unit/integration tests + {n} E2E scenarios"),
    ),
    statements="**Total statements:**",
    covered="**Covered:**",
)

PT_BR = Locale(
    source="Fonte",
    columns={"Testes": "Tests", "Cenários": "Scenarios", "Steps": "Steps"},
    summary=(
        ("Unit Tests", "**Testes Unitários**: {n} testes"),
        ("Integration Tests", "**Testes de Integração**: {n} testes"),
        ("E2E Tests", "**Testes E2E**: {n} cenários, {n} steps"),
        ("Total", "**Total**: {n} testes unitários/de integração + {n} cenários E2E"),
    ),
    statements="**Total de statements:**",
    covered="**Cobertos:**",
)

ES = Locale(
    source="Fuente",
    columns={"Pruebas": "Tests", "Escenarios": "Scenarios", "Steps": "Steps"},
    summary=(
        ("Unit Tests", "**Pruebas Unitarias**: {n} pruebas"),
        ("Integration Tests", "**Pruebas de Integración**: {n} pruebas"),
        ("E2E Tests", "**Pruebas E2E**: {n} escenarios, {n} steps"),
        (
            "Total",
            "**Total**: {n} pruebas unitarias/de integración + {n} escenarios E2E",
        ),
    ),
    statements="**Total de statements:**",
    covered="**Cubiertos:**",
)

TRANSLATIONS = {"README.pt-BR.md": PT_BR, "README.es.md": ES}

MARKER = re.compile(r"<!-- translation-source: README\.md sha256:([0-9a-f]{64}) -->")

Counts = dict[str, dict[str, int]]


class CollectionError(Exception):
    """pytest or behave could not list the tests: nothing to compare with."""


def parse_pytest_counts(output: str) -> Counts:
    """Read the "path: count" lines of `pytest --co -qq`."""
    return {
        path: {"Tests": int(count)}
        for path, count in re.findall(r"^(\S+\.py): (\d+)$", output, re.MULTILINE)
    }


def parse_behave_counts(report: list[dict]) -> Counts:
    """Count scenarios and their steps (background included) per feature file."""
    counts = {}
    for feature in report:
        path = feature["location"].rsplit(":", 1)[0]
        scenarios = [
            element
            for element in feature.get("elements", [])
            if element["type"] == "scenario"
        ]
        counts[path] = {
            "Scenarios": len(scenarios),
            "Steps": sum(len(scenario.get("steps", [])) for scenario in scenarios),
        }
    return counts


def collect_counts() -> Counts:
    """Collect the test count of every pytest file and feature file."""
    pytest_run = subprocess.run(
        ["poetry", "run", "pytest", "--co", "-qq"],
        capture_output=True,
        text=True,
        check=False,
    )
    if pytest_run.returncode != 0:
        raise CollectionError(f"pytest --co exited {pytest_run.returncode}")

    with tempfile.TemporaryDirectory() as folder:
        report_path = Path(folder) / "behave.json"
        behave_run = subprocess.run(
            ["poetry", "run", "behave", "--dry-run", "-f", "json", "-o", report_path],
            capture_output=True,
            text=True,
            check=False,
        )
        if behave_run.returncode != 0:
            raise CollectionError(f"behave --dry-run exited {behave_run.returncode}")
        report = json.loads(report_path.read_text(encoding="utf-8"))

    return parse_pytest_counts(pytest_run.stdout) | parse_behave_counts(report)


def _cells(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def _set_cells(line: str, values: dict[int, str]) -> str:
    """Replace cells by index, keeping the rest of the row byte for byte."""
    parts = line.split("|")
    for index, value in values.items():
        parts[index + 1] = f" {value} "
    return "|".join(parts)


class _TableUpdater:
    """Rewrites the metric cells of the tables that have a Source column."""

    def __init__(self, counts: Counts, locale: Locale):
        self.counts = counts
        self.locale = locale
        self.used: set[str] = set()
        self.errors: list[str] = []
        self.columns: dict[str, int] = {}
        self.source = -1
        self.totals: dict[str, int] = {}

    def start_table(self, header: list[str]) -> None:
        """Remember where the Source and metric columns of this table are."""
        self.source = header.index(self.locale.source)
        self.columns = {
            self.locale.columns[name]: index
            for index, name in enumerate(header)
            if name in self.locale.columns
        }
        self.totals = dict.fromkeys(self.columns, 0)

    def row(self, line: str) -> str:
        """Return the row with its metric cells rewritten."""
        cells = _cells(line)
        label = cells[0].strip("*")
        if label == "TOTAL":
            return _set_cells(
                line,
                {i: f"**{self.totals[name]}**" for name, i in self.columns.items()},
            )

        sums = self._sum_sources(label, re.findall(r"`([^`]+)`", cells[self.source]))
        if sums is None:
            return line
        for name, value in sums.items():
            self.totals[name] += value
        return _set_cells(
            line, {i: str(sums[name]) for name, i in self.columns.items()}
        )

    def _sum_sources(self, label: str, sources: list[str]) -> dict[str, int] | None:
        if not sources:
            self.errors.append(f"{label}: no source file")
            return None
        sums = dict.fromkeys(self.columns, 0)
        for source in sources:
            if source not in self.counts:
                self.errors.append(f"{label}: unknown source {source}")
                return None
            if source in self.used:
                self.errors.append(f"{label}: {source} is already in another row")
                return None
            self.used.add(source)
            for name in self.columns:
                if name not in self.counts[source]:
                    self.errors.append(f"{label}: {source} has no {name} count")
                    return None
                sums[name] += self.counts[source][name]
        return sums


def update_tables(
    text: str, counts: Counts, locale: Locale = EN
) -> tuple[str, list[str]]:
    """Rewrite each Source-table row from the counts of its source files."""
    updater = _TableUpdater(counts, locale)
    lines = text.split("\n")
    in_table = False
    for number, line in enumerate(lines):
        if not line.startswith("|"):
            in_table = False
        elif locale.source in _cells(line):
            updater.start_table(_cells(line))
            in_table = True
        elif in_table and not set(line) <= set("|-: "):
            lines[number] = updater.row(line)

    missing = sorted(set(counts) - updater.used)
    errors = updater.errors + [f"{path} is not in any README table" for path in missing]
    return "\n".join(lines), errors


def _sub_numbers(text: str, template: str, values: tuple[int, ...]) -> tuple[str, int]:
    parts = template.split("{n}")
    pattern = r"\d+".join(re.escape(part) for part in parts)
    replacement = parts[0] + "".join(
        f"{value}{part}" for value, part in zip(values, parts[1:])
    )
    return re.subn(pattern, lambda _: replacement, text, count=1)


def update_summary(
    text: str, counts: Counts, locale: Locale = EN
) -> tuple[str, list[str]]:
    """Rewrite the layer summary lines from the totals of the counts."""

    def total(name: str, integration: bool | None = None) -> int:
        return sum(
            metrics.get(name, 0)
            for path, metrics in counts.items()
            if integration is None or path.startswith(INTEGRATION_DIR) == integration
        )

    values = {
        "Unit Tests": (total("Tests", integration=False),),
        "Integration Tests": (total("Tests", integration=True),),
        "E2E Tests": (total("Scenarios"), total("Steps")),
        "Total": (total("Tests"), total("Scenarios")),
    }
    errors = []
    for label, template in locale.summary:
        text, found = _sub_numbers(text, template, values[label])
        if not found:
            errors.append(f"Summary line not found: {label}")
    return text, errors


def get_coverage_statements() -> tuple[int, int]:
    """Get total statements and covered from coverage.xml.

    Returns:
        Tuple of (total_statements, covered_statements); (0, 0) without it.
    """
    coverage_file = Path("coverage.xml")
    if not coverage_file.exists():
        print(
            "WARN: coverage.xml not found, skipping coverage validation",
            file=sys.stderr,
        )
        return (0, 0)

    root = ET.parse(coverage_file).getroot()
    # <coverage line-rate="0.99" lines-covered="315" lines-valid="316">
    lines_covered = int(root.attrib.get("lines-covered", 0))
    lines_valid = int(root.attrib.get("lines-valid", 0))
    return (lines_valid, lines_covered)


def check_coverage(
    text: str, actual: tuple[int, int], locale: Locale = EN
) -> list[str]:
    """Compare the README coverage statements with coverage.xml."""
    if actual == (0, 0):
        return []
    errors = []
    checks = (
        ("Total statements", locale.statements, actual[0]),
        ("Covered statements", locale.covered, actual[1]),
    )
    for label, words, value in checks:
        match = re.search(re.escape(words) + r"\s*(\d+)", text)
        shown = int(match.group(1)) if match else None
        if shown != value:
            errors.append(f"{label}: README shows {shown}, actual is {value}")
    return errors


def source_fingerprint(readme: str, counts: Counts) -> str:
    """Hash README.md with the numbers the hook owns masked.

    Those numbers reach the translations through the hook itself; any other
    change to README.md is text a human has to translate.
    """
    zeros = {path: dict.fromkeys(metrics, 0) for path, metrics in counts.items()}
    text, _ = update_tables(readme, zeros)
    text, _ = update_summary(text, zeros)
    for words in (EN.statements, EN.covered):
        text = re.sub(re.escape(words) + r".*", words, text)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def check_translation_source(path: str, text: str, fingerprint: str) -> list[str]:
    """Fail a translation made from another version of README.md."""
    marker = f"<!-- translation-source: README.md sha256:{fingerprint} -->"
    match = MARKER.search(text)
    if match is None:
        return [f"{path} has no translation-source marker; add {marker}"]
    if match.group(1) != fingerprint:
        return [
            f"{path} was translated from an older README.md: translate what "
            f"changed (git log -p -- README.md), then set its marker to {marker}"
        ]
    return []


def _update_readme(
    path: str, counts: Counts, locale: Locale, coverage: tuple[int, int]
) -> tuple[str, list[str]]:
    """Rewrite one README file; return its new text and what needs a human."""
    readme_path = Path(path)
    original = readme_path.read_text(encoding="utf-8")
    text, errors = update_tables(original, counts, locale)
    text, summary_errors = update_summary(text, counts, locale)
    errors += summary_errors + check_coverage(text, coverage, locale)
    errors = [f"{path}: {error}" for error in errors]
    if text != original:
        readme_path.write_text(text, encoding="utf-8")
        errors.append(
            f"{path} metrics updated from the collected tests: review and stage it."
        )
    return text, errors


def main() -> int:
    """Rewrite the README metrics; fail if one changed or needs a human fix."""
    try:
        counts = collect_counts()
    except CollectionError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1

    coverage = get_coverage_statements()
    readme, errors = _update_readme(README, counts, EN, coverage)
    fingerprint = source_fingerprint(readme, counts)
    for path, locale in TRANSLATIONS.items():
        if not Path(path).exists():
            errors.append(f"{path} not found")
            continue
        text, translation_errors = _update_readme(path, counts, locale, coverage)
        errors += translation_errors + check_translation_source(path, text, fingerprint)

    if errors:
        print("\nERROR: the README metrics need a look:\n", file=sys.stderr)
        print("\n".join(f"  {error}" for error in errors), file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
