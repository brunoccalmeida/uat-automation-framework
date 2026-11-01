"""Tests for the README metrics hook (scripts/validate_readme_metrics.py).

Each table row names its test files in a Source column; the hook rewrites the
counts of every row, the TOTAL rows and the layer summary from the collected
counts, and fails when it changed something (#34: a check of the total alone
accepted any split that summed right). The translations (#39) get the same
rewrite with their own labels, and fail when README.md changed after them.
"""

import re
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from scripts import validate_readme_metrics as validator

PRE_COMMIT = Path(__file__).resolve().parent.parent / ".pre-commit-config.yaml"

COUNTS = {
    "tests/test_base_page.py": {"Tests": 23},
    "tests/test_login_page.py": {"Tests": 14},
    "tests/integration/test_cart_page_integration.py": {"Tests": 10},
    "features/cart.feature": {"Scenarios": 6, "Steps": 35},
    "features/cart_neg.feature": {"Scenarios": 5, "Steps": 30},
}

UNIT_TABLE = """\
| Module | Source | Tests | Coverage | Status |
|--------|--------|-------|----------|--------|
| **BasePage** | `tests/test_base_page.py` | {base} | 100% | ✅ Complete |
| **LoginPage** | `tests/test_login_page.py` | 14 | 100% | ✅ Complete |
| **TOTAL** | | **{total}** | **100%** | **Complete** |
"""

INTEGRATION_TABLE = """\
| Module | Source | Tests | Browser |
|--------|--------|-------|---------|
| **CartPage** | `tests/integration/test_cart_page_integration.py` | 10 | Chrome |
| **TOTAL** | | **10** | **Real** |
"""

BEHAVE_TABLE = """\
| Feature | Source | Scenarios | Steps |
|---------|--------|-----------|-------|
| **Cart** | `features/cart.feature`, `features/cart_neg.feature` | {sc} | {st} |
| **TOTAL** | | **11** | **65** |
"""

SUMMARY = """\
- **Unit Tests**: {unit} tests (framework components)
- **Integration Tests**: 10 tests (Page Objects + real browser)
- **E2E Tests**: 11 scenarios, 65 steps (complete user journeys)
- **Total**: 47 unit/integration tests + 11 E2E scenarios
"""


def _readme(base=23, total=37, scenarios=11, steps=65, unit=37):
    return "\n".join(
        [
            UNIT_TABLE.format(base=base, total=total),
            INTEGRATION_TABLE,
            BEHAVE_TABLE.format(sc=scenarios, st=steps),
            SUMMARY.format(unit=unit),
        ]
    )


PT_TABLE = """\
| Módulo | Fonte | Testes | Cobertura |
|--------|-------|--------|-----------|
| **BasePage** | `tests/test_base_page.py` | {base} | 100% |
| **LoginPage** | `tests/test_login_page.py` | 14 | 100% |
| **TOTAL** | | **{total}** | **100%** |
"""

PT_INTEGRATION_TABLE = """\
| Módulo | Fonte | Testes | Navegador |
|--------|-------|--------|-----------|
| **CartPage** | `tests/integration/test_cart_page_integration.py` | 10 | Chrome |
| **TOTAL** | | **10** | **Real** |
"""

PT_BEHAVE_TABLE = """\
| Feature | Fonte | Cenários | Steps |
|---------|-------|----------|-------|
| **Carrinho** | `features/cart.feature`, `features/cart_neg.feature` | 11 | 65 |
| **TOTAL** | | **11** | **65** |
"""

PT_SUMMARY = """\
- **Testes Unitários**: {unit} testes (componentes do framework)
- **Testes de Integração**: 10 testes (Page Objects + navegador real)
- **Testes E2E**: 11 cenários, 65 steps (jornadas completas de usuário)
- **Total**: 47 testes unitários/de integração + 11 cenários E2E
"""


def _translation(marker, base=23, total=37, unit=37):
    return "\n".join(
        [
            marker,
            PT_TABLE.format(base=base, total=total),
            PT_INTEGRATION_TABLE,
            PT_BEHAVE_TABLE,
            PT_SUMMARY.format(unit=unit),
        ]
    )


def _fingerprint(readme=None):
    return validator.source_fingerprint(readme or _readme(), COUNTS)


def _marker(readme=None):
    return f"<!-- translation-source: README.md sha256:{_fingerprint(readme)} -->"


class TestParsePytestCounts:
    """`pytest --co -qq` prints one "path: count" line per test file."""

    def test_reads_count_per_file(self):
        output = (
            "tests/integration/test_cart_page_integration.py: 10\n"
            "tests/test_base_page.py: 23\n"
        )

        assert validator.parse_pytest_counts(output) == {
            "tests/integration/test_cart_page_integration.py": {"Tests": 10},
            "tests/test_base_page.py": {"Tests": 23},
        }

    def test_ignores_other_lines(self):
        output = "tests/test_base_page.py: 23\n\nno tests ran in 0.20s\n"

        assert validator.parse_pytest_counts(output) == {
            "tests/test_base_page.py": {"Tests": 23}
        }


class TestParseBehaveCounts:
    """The JSON report has one entry per feature file, steps per scenario."""

    def test_counts_scenarios_and_their_steps_per_file(self):
        report = [
            {
                "location": "features/cart.feature:2",
                "elements": [
                    {"type": "background", "steps": [{}, {}]},
                    {"type": "scenario", "steps": [{}, {}, {}]},
                    {"type": "scenario", "steps": [{}, {}]},
                ],
            }
        ]

        assert validator.parse_behave_counts(report) == {
            "features/cart.feature": {"Scenarios": 2, "Steps": 5}
        }

    def test_feature_without_scenarios_counts_zero(self):
        report = [{"location": "features/empty.feature:1"}]

        assert validator.parse_behave_counts(report) == {
            "features/empty.feature": {"Scenarios": 0, "Steps": 0}
        }


class TestUpdateTables:
    """Each row is the sum of its sources; TOTAL is the sum of the rows."""

    def test_accurate_tables_are_unchanged(self):
        readme = _readme()

        assert validator.update_tables(readme, COUNTS) == (readme, [])

    def test_wrong_split_with_right_total_is_fixed(self):
        """The #34 case: rows wrong, the sum still matching."""
        readme = _readme(base=30, total=37)

        updated, errors = validator.update_tables(readme, COUNTS)

        assert not errors
        assert updated == _readme()

    def test_wrong_total_is_fixed(self):
        updated, _ = validator.update_tables(_readme(total=99), COUNTS)

        assert updated == _readme()

    def test_row_sums_all_of_its_sources(self):
        updated, _ = validator.update_tables(_readme(scenarios=8, steps=59), COUNTS)

        assert updated == _readme()

    def test_file_in_no_row_is_an_error(self):
        counts = dict(COUNTS, **{"tests/test_new.py": {"Tests": 3}})

        _, errors = validator.update_tables(_readme(), counts)

        assert errors == ["tests/test_new.py is not in any README table"]

    def test_unknown_source_is_an_error(self):
        readme = _readme().replace("tests/test_login_page.py", "tests/test_gone.py")

        _, errors = validator.update_tables(readme, COUNTS)

        assert "LoginPage: unknown source tests/test_gone.py" in errors

    def test_source_in_two_rows_is_an_error(self):
        readme = _readme().replace(
            "tests/test_login_page.py", "tests/test_base_page.py"
        )

        _, errors = validator.update_tables(readme, COUNTS)

        assert "LoginPage: tests/test_base_page.py is already in another row" in errors

    def test_row_without_source_is_an_error(self):
        readme = _readme().replace("`tests/test_login_page.py`", "")

        _, errors = validator.update_tables(readme, COUNTS)

        assert "LoginPage: no source file" in errors

    def test_source_without_the_column_metric_is_an_error(self):
        readme = _readme().replace("tests/test_login_page.py", "features/cart.feature")
        counts = {k: v for k, v in COUNTS.items() if k != "tests/test_login_page.py"}

        _, errors = validator.update_tables(readme, counts)

        assert "LoginPage: features/cart.feature has no Tests count" in errors


class TestLocalizedTables:
    """A translation names the Source and metric columns in its own language."""

    def test_accurate_translated_tables_are_unchanged(self):
        readme = _translation("")

        assert validator.update_tables(readme, COUNTS, validator.PT_BR) == (readme, [])

    def test_outdated_translated_row_and_total_are_fixed(self):
        readme = _translation("", base=19, total=33)

        updated, errors = validator.update_tables(readme, COUNTS, validator.PT_BR)

        assert not errors
        assert updated == _translation("")


class TestUpdateSummary:
    """The layer summary splits unit/integration by folder, as the CI does."""

    def test_accurate_summary_is_unchanged(self):
        readme = _readme()

        assert validator.update_summary(readme, COUNTS) == (readme, [])

    def test_outdated_summary_is_fixed(self):
        readme = _readme().replace("10 tests", "75 tests").replace("47 unit", "1 unit")
        readme = readme.replace("11 scenarios, 65", "8 scenarios, 59")

        updated, errors = validator.update_summary(readme, COUNTS)

        assert not errors
        assert updated == _readme()

    def test_missing_summary_line_is_an_error(self):
        readme = _readme().replace("**E2E Tests**", "**End-to-end**")

        _, errors = validator.update_summary(readme, COUNTS)

        assert errors == ["Summary line not found: E2E Tests"]


class TestLocalizedSummary:
    """The summary lines of a translation are found by its own wording."""

    def test_outdated_translated_summary_is_fixed(self):
        readme = _translation("", unit=132)

        updated, errors = validator.update_summary(readme, COUNTS, validator.PT_BR)

        assert not errors
        assert updated == _translation("")

    @pytest.mark.parametrize("locale", [validator.PT_BR, validator.ES])
    def test_templates_keep_the_number_slots_of_english(self, locale):
        english = dict(validator.EN.summary)

        assert {label for label, _ in locale.summary} == set(english)
        for label, template in locale.summary:
            assert template.count("{n}") == english[label].count("{n}")


class TestCheckCoverage:
    """Coverage is only checked (it needs a coverage.xml), never rewritten."""

    README = "- **Total statements:** 346\n- **Covered:** 345 (99%)\n"

    def test_matching_coverage_passes(self):
        assert not validator.check_coverage(self.README, (346, 345))

    def test_outdated_coverage_fails_with_both_values(self):
        errors = validator.check_coverage(self.README, (350, 349))

        assert errors == [
            "Total statements: README shows 346, actual is 350",
            "Covered statements: README shows 345, actual is 349",
        ]

    def test_missing_coverage_report_is_skipped(self):
        """get_coverage_statements returns (0, 0) without a coverage.xml."""
        assert not validator.check_coverage(self.README, (0, 0))


class TestLocalizedCoverage:
    """A translation shows the coverage under its own labels."""

    def test_outdated_translated_coverage_fails(self):
        readme = "- **Total de statements:** 346\n- **Cobertos:** 345 (99%)\n"

        errors = validator.check_coverage(readme, (350, 349), validator.PT_BR)

        assert errors == [
            "Total statements: README shows 346, actual is 350",
            "Covered statements: README shows 345, actual is 349",
        ]


class TestSourceFingerprint:
    """The hash of the README.md a translation was made from.

    The numbers the hook writes are masked: they reach the translations through
    the hook itself, so a new test must not mark every translation as stale.
    """

    COVERAGE = "- **Total statements:** {total}\n- **Covered:** {covered} ({pct}%)\n"

    def test_new_counts_keep_the_fingerprint(self):
        stale = _readme(base=30, total=44, scenarios=8, steps=59, unit=44)
        stale += self.COVERAGE.format(total=300, covered=290, pct=97)
        fresh = _readme() + self.COVERAGE.format(total=346, covered=345, pct=99)

        assert validator.source_fingerprint(stale, COUNTS) == (
            validator.source_fingerprint(fresh, COUNTS)
        )

    def test_new_text_changes_the_fingerprint(self):
        edited = _readme().replace("framework components", "framework parts")

        assert validator.source_fingerprint(edited, COUNTS) != (
            validator.source_fingerprint(_readme(), COUNTS)
        )


class TestCheckTranslationSource:
    """A translation fails when README.md changed after it was translated."""

    def test_translation_of_the_current_readme_passes(self):
        assert not validator.check_translation_source(
            "README.pt-BR.md", _translation(_marker()), _fingerprint()
        )

    def test_translation_of_an_older_readme_fails_with_the_new_marker(self):
        older = _marker(_readme().replace("framework components", "old text"))

        errors = validator.check_translation_source(
            "README.pt-BR.md", _translation(older), _fingerprint()
        )

        assert len(errors) == 1
        assert "README.pt-BR.md was translated from an older README.md" in errors[0]
        assert _marker() in errors[0]

    def test_translation_without_marker_fails(self):
        errors = validator.check_translation_source(
            "README.pt-BR.md", _translation(""), _fingerprint()
        )

        assert len(errors) == 1
        assert "README.pt-BR.md has no translation-source marker" in errors[0]


@pytest.fixture(name="readme_path")
def fixture_readme_path(tmp_path, monkeypatch):
    """Run from a folder with a README.md and one translation, as the hook does."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(validator, "TRANSLATIONS", {"README.pt-BR.md": validator.PT_BR})
    (tmp_path / "README.pt-BR.md").write_text(_translation(_marker()), encoding="utf-8")
    return tmp_path / "README.md"


@pytest.fixture(name="translation_path")
def fixture_translation_path(readme_path):
    """The translation next to the README.md of readme_path."""
    return readme_path.parent / "README.pt-BR.md"


class TestMain:
    """The hook rewrites README.md and fails when it changed it (like black)."""

    @staticmethod
    def _main(counts=None):
        with (
            patch.object(validator, "collect_counts", return_value=counts or COUNTS),
            patch.object(validator, "get_coverage_statements", return_value=(0, 0)),
        ):
            return validator.main([])

    def test_accurate_readme_passes_untouched(self, readme_path):
        readme_path.write_text(_readme(), encoding="utf-8")

        assert self._main() == 0
        assert readme_path.read_text(encoding="utf-8") == _readme()

    def test_outdated_readme_is_rewritten_and_fails(self, readme_path, capsys):
        readme_path.write_text(_readme(base=30), encoding="utf-8")

        assert self._main() == 1
        assert readme_path.read_text(encoding="utf-8") == _readme()
        assert "README.md metrics updated" in capsys.readouterr().err

    def test_second_run_after_the_fix_passes(self, readme_path):
        readme_path.write_text(_readme(base=30), encoding="utf-8")
        self._main()

        assert self._main() == 0

    def test_errors_fail_and_are_reported(self, readme_path, capsys):
        readme_path.write_text(_readme(), encoding="utf-8")
        counts = dict(COUNTS, **{"tests/test_new.py": {"Tests": 3}})

        assert self._main(counts) == 1
        assert "tests/test_new.py is not in any README table" in capsys.readouterr().err

    def test_collection_failure_fails_instead_of_skipping(self, readme_path, capsys):
        readme_path.write_text(_readme(), encoding="utf-8")
        with patch.object(
            validator,
            "collect_counts",
            side_effect=validator.CollectionError("pytest --co exited 2"),
        ):
            assert validator.main([]) == 1
        assert "pytest --co exited 2" in capsys.readouterr().err

    def test_outdated_translation_is_rewritten_and_fails(
        self, readme_path, translation_path, capsys
    ):
        readme_path.write_text(_readme(), encoding="utf-8")
        translation_path.write_text(
            _translation(_marker(), base=19, total=33, unit=132), encoding="utf-8"
        )

        assert self._main() == 1
        assert translation_path.read_text(encoding="utf-8") == _translation(_marker())
        assert "README.pt-BR.md metrics updated" in capsys.readouterr().err

    def test_readme_edited_after_the_translation_fails(self, readme_path, capsys):
        readme_path.write_text(
            _readme().replace("framework components", "new text"), encoding="utf-8"
        )

        assert self._main() == 1
        assert "translated from an older README.md" in capsys.readouterr().err

    def test_missing_translation_fails(self, readme_path, translation_path, capsys):
        readme_path.write_text(_readme(), encoding="utf-8")
        translation_path.unlink()

        assert self._main() == 1
        assert "README.pt-BR.md not found" in capsys.readouterr().err


COVERAGE_XML = '<coverage lines-valid="{total}" lines-covered="{covered}"/>'


class TestCoverageMode:
    """CI checks the coverage where coverage.xml exists: the test job (#87).

    The hook runs in the lint job, which has no coverage.xml, so there it
    skips the check; with --coverage a missing report fails instead.
    """

    EN_COVERAGE = "- **Total statements:** 346\n- **Covered:** 345 (99%)\n"
    PT_COVERAGE = "- **Total de statements:** 346\n- **Cobertos:** 345 (99%)\n"

    @pytest.fixture(autouse=True)
    def _readmes(self, readme_path, translation_path):
        readme_path.write_text(self.EN_COVERAGE, encoding="utf-8")
        translation_path.write_text(self.PT_COVERAGE, encoding="utf-8")

    @staticmethod
    def _main(total=346, covered=345):
        Path("coverage.xml").write_text(
            COVERAGE_XML.format(total=total, covered=covered), encoding="utf-8"
        )
        with patch.object(validator, "collect_counts") as collect:
            result = validator.main(["--coverage", "coverage.xml"])
        collect.assert_not_called()
        return result

    def test_matching_coverage_passes(self):
        assert self._main() == 0

    def test_outdated_coverage_fails_for_every_readme(self, capsys):
        assert self._main(total=350, covered=349) == 1

        err = capsys.readouterr().err
        assert "README.md: Total statements: README shows 346, actual is 350" in err
        assert "README.pt-BR.md: Covered statements: README shows 345" in err

    def test_outdated_readme_is_not_rewritten(self, readme_path):
        self._main(total=350, covered=349)

        assert readme_path.read_text(encoding="utf-8") == self.EN_COVERAGE

    def test_missing_report_fails_instead_of_skipping(self, capsys):
        assert validator.main(["--coverage", "coverage.xml"]) == 1
        assert "coverage.xml not found" in capsys.readouterr().err


class TestCiCoverageStep:
    """The test job checks the README coverage after it writes coverage.xml."""

    WORKFLOW = PRE_COMMIT.parent / ".github" / "workflows" / "tests.yml"

    def test_check_runs_after_the_coverage_report(self):
        steps = yaml.safe_load(self.WORKFLOW.read_text(encoding="utf-8"))["jobs"][
            "test"
        ]["steps"]
        runs = [step.get("run", "") for step in steps]
        report = next(i for i, run in enumerate(runs) if "--cov-report=xml" in run)
        check = next(
            i
            for i, run in enumerate(runs)
            if "validate_readme_metrics.py --coverage coverage.xml" in run
        )

        assert check > report


class TestPreCommitHook:
    """A metric goes stale when a test changes, not only when README.md does."""

    @pytest.mark.parametrize(
        "path",
        [
            "README.md",
            "README.pt-BR.md",
            "README.es.md",
            "tests/test_base_page.py",
            "tests/integration/test_cart_page_integration.py",
            "features/cart.feature",
        ],
    )
    def test_hook_runs_when_counted_files_change(self, path):
        config = yaml.safe_load(PRE_COMMIT.read_text(encoding="utf-8"))
        hooks = {hook["id"]: hook for repo in config["repos"] for hook in repo["hooks"]}

        assert re.search(hooks["validate-readme-metrics"]["files"], path)
