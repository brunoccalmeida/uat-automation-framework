"""Tests for the README metrics comparison (scripts/validate_readme_metrics.py).

The collectors (pytest, behave, coverage) are mocked: these tests cover how
the README values are compared with the actual ones and reported.
"""

from unittest.mock import patch

import pytest

from scripts import validate_readme_metrics as validator

ACTUAL = {
    "pytest_count": 280,
    "scenario_count": 55,
    "total_statements": 346,
    "covered_statements": 343,
}


@pytest.fixture(name="readme_dir")
def fixture_readme_dir(tmp_path, monkeypatch):
    """Run from a folder that has a README.md, as the script expects."""
    (tmp_path / "README.md").write_text("", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    return tmp_path


def _validate(readme, actual=None):
    actual = actual or ACTUAL
    with (
        patch.object(
            validator, "get_pytest_count", return_value=actual["pytest_count"]
        ),
        patch.object(
            validator,
            "get_behave_scenario_count",
            return_value=actual["scenario_count"],
        ),
        patch.object(
            validator,
            "get_coverage_statements",
            return_value=(actual["total_statements"], actual["covered_statements"]),
        ),
        patch.object(validator, "extract_readme_metrics", return_value=readme),
    ):
        return validator.validate_metrics()


@pytest.mark.usefixtures("readme_dir")
class TestValidateMetrics:
    """Each README metric is compared with the actual value."""

    def test_matching_metrics_pass(self):
        assert _validate(dict(ACTUAL)) is True

    @pytest.mark.parametrize(
        "key, label",
        [
            ("pytest_count", "Pytest count"),
            ("scenario_count", "Scenario count"),
            ("total_statements", "Total statements"),
            ("covered_statements", "Covered statements"),
        ],
    )
    def test_outdated_metric_fails_with_both_values(self, key, label, capsys):
        readme = dict(ACTUAL, **{key: 1})

        assert _validate(readme) is False
        expected = f"  ERROR: {label}: README shows 1, actual is {ACTUAL[key]}"
        assert expected in capsys.readouterr().err

    def test_metric_that_could_not_be_collected_is_skipped(self):
        """A collector returns 0 on failure; it must not flag the README."""
        actual = dict(ACTUAL, pytest_count=0)
        assert _validate(dict(ACTUAL), actual) is True
