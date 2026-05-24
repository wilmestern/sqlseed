"""Tests for sqlseed.row_summarizer."""

from __future__ import annotations

import pytest

from sqlseed.row_summarizer import (
    ColumnSummary,
    RowSummary,
    summarize_rows,
)


@pytest.fixture()
def sample_rows():
    return [
        {"id": 1, "name": "Alice", "email": "alice@example.com", "age": 30},
        {"id": 2, "name": "Bob", "email": None, "age": 25},
        {"id": 3, "name": "Alice", "email": "carol@example.com", "age": None},
    ]


def test_summarize_rows_returns_row_summary(sample_rows):
    result = summarize_rows("users", sample_rows)
    assert isinstance(result, RowSummary)


def test_summarize_rows_correct_row_count(sample_rows):
    result = summarize_rows("users", sample_rows)
    assert result.row_count == 3


def test_summarize_rows_table_name(sample_rows):
    result = summarize_rows("users", sample_rows)
    assert result.table == "users"


def test_summarize_rows_column_count(sample_rows):
    result = summarize_rows("users", sample_rows)
    assert len(result.column_summaries) == 4


def test_summarize_rows_null_count(sample_rows):
    result = summarize_rows("users", sample_rows)
    assert result.get("email").null_count == 1
    assert result.get("age").null_count == 1


def test_summarize_rows_null_rate(sample_rows):
    result = summarize_rows("users", sample_rows)
    cs = result.get("email")
    assert abs(cs.null_rate - 1 / 3) < 1e-6


def test_summarize_rows_unique_count(sample_rows):
    result = summarize_rows("users", sample_rows)
    assert result.get("name").unique_count == 2  # Alice, Bob
    assert result.get("id").unique_count == 3


def test_summarize_rows_sample_values_not_empty(sample_rows):
    result = summarize_rows("users", sample_rows)
    assert len(result.get("name").sample_values) > 0


def test_summarize_rows_sample_values_max_three(sample_rows):
    rows = [{"x": i} for i in range(10)]
    result = summarize_rows("t", rows)
    assert len(result.get("x").sample_values) <= 3


def test_summarize_rows_empty_input():
    result = summarize_rows("empty", [])
    assert result.row_count == 0
    assert result.column_summaries == {}


def test_row_summary_get_returns_none_for_missing(sample_rows):
    result = summarize_rows("users", sample_rows)
    assert result.get("nonexistent") is None


def test_row_summary_get_case_insensitive(sample_rows):
    result = summarize_rows("users", sample_rows)
    assert result.get("EMAIL") is not None


def test_row_summary_as_dict_keys(sample_rows):
    result = summarize_rows("users", sample_rows)
    d = result.as_dict()
    assert "table" in d
    assert "row_count" in d
    assert "columns" in d


def test_column_summary_str_contains_column():
    cs = ColumnSummary(column="email", count=10, null_count=2, unique_count=8)
    assert "email" in str(cs)


def test_row_summary_str_contains_table(sample_rows):
    result = summarize_rows("users", sample_rows)
    assert "users" in str(result)
