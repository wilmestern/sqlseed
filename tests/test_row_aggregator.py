"""Tests for sqlseed.row_aggregator."""

import pytest

from sqlseed.row_aggregator import (
    AggregationReport,
    AggregationResult,
    aggregate_column,
    aggregate_rows,
    get_aggregation_fn,
)


@pytest.fixture
def sample_rows():
    return [
        {"id": 1, "score": 10.0, "label": "a", "note": None},
        {"id": 2, "score": 20.0, "label": "b", "note": None},
        {"id": 3, "score": 30.0, "label": "a", "note": "hi"},
        {"id": 4, "score": None, "label": "c", "note": None},
    ]


# --- get_aggregation_fn ---

def test_get_aggregation_fn_returns_callable():
    fn = get_aggregation_fn("count")
    assert callable(fn)


def test_get_aggregation_fn_case_insensitive():
    fn_lower = get_aggregation_fn("sum")
    fn_upper = get_aggregation_fn("SUM")
    assert fn_lower([1, 2, 3]) == fn_upper([1, 2, 3])


def test_get_aggregation_fn_unknown_raises():
    with pytest.raises(ValueError, match="Unknown aggregation operation"):
        get_aggregation_fn("median")


# --- aggregate_column ---

def test_aggregate_column_count(sample_rows):
    result = aggregate_column(sample_rows, "score", "count")
    assert result.value == 4


def test_aggregate_column_sum(sample_rows):
    result = aggregate_column(sample_rows, "score", "sum")
    assert result.value == 60.0


def test_aggregate_column_avg(sample_rows):
    result = aggregate_column(sample_rows, "score", "avg")
    assert result.value == 20.0


def test_aggregate_column_min(sample_rows):
    result = aggregate_column(sample_rows, "score", "min")
    assert result.value == 10.0


def test_aggregate_column_max(sample_rows):
    result = aggregate_column(sample_rows, "score", "max")
    assert result.value == 30.0


def test_aggregate_column_null_count(sample_rows):
    result = aggregate_column(sample_rows, "note", "null_count")
    assert result.value == 3


def test_aggregate_column_distinct_count(sample_rows):
    result = aggregate_column(sample_rows, "label", "distinct_count")
    assert result.value == 3


def test_aggregate_column_result_has_correct_metadata(sample_rows):
    result = aggregate_column(sample_rows, "id", "count")
    assert result.column == "id"
    assert result.operation == "count"


def test_aggregate_column_min_all_none():
    rows = [{"x": None}, {"x": None}]
    result = aggregate_column(rows, "x", "min")
    assert result.value is None


# --- aggregate_rows ---

def test_aggregate_rows_returns_report(sample_rows):
    specs = [{"column": "score", "operation": "sum"}]
    report = aggregate_rows(sample_rows, specs)
    assert isinstance(report, AggregationReport)


def test_aggregate_rows_multiple_specs(sample_rows):
    specs = [
        {"column": "score", "operation": "sum"},
        {"column": "id", "operation": "count"},
    ]
    report = aggregate_rows(sample_rows, specs)
    assert len(report.results) == 2


def test_aggregate_rows_get_existing(sample_rows):
    specs = [{"column": "score", "operation": "max"}]
    report = aggregate_rows(sample_rows, specs)
    assert report.get("score", "max") == 30.0


def test_aggregate_rows_get_missing_returns_none(sample_rows):
    report = aggregate_rows(sample_rows, [])
    assert report.get("score", "sum") is None


def test_aggregate_rows_as_dict(sample_rows):
    specs = [
        {"column": "score", "operation": "sum"},
        {"column": "label", "operation": "distinct_count"},
    ]
    report = aggregate_rows(sample_rows, specs)
    d = report.as_dict()
    assert "sum(score)" in d
    assert "distinct_count(label)" in d


def test_aggregate_rows_empty_rows():
    report = aggregate_rows([], [{"column": "x", "operation": "count"}])
    assert report.get("x", "count") == 0
