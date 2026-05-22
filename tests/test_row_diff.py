"""Tests for sqlseed.row_diff."""

import pytest
from sqlseed.row_diff import (
    FieldDiff,
    RowDiff,
    DiffReport,
    diff_row,
    diff_rows,
)


# ---------------------------------------------------------------------------
# FieldDiff
# ---------------------------------------------------------------------------

def test_field_diff_str_includes_column():
    fd = FieldDiff(column="email", left="a@a.com", right="b@b.com")
    assert "email" in str(fd)


def test_field_diff_str_includes_values():
    fd = FieldDiff(column="age", left=30, right=31)
    assert "30" in str(fd)
    assert "31" in str(fd)


# ---------------------------------------------------------------------------
# RowDiff
# ---------------------------------------------------------------------------

def test_row_diff_has_changes_true_when_diffs_present():
    rd = RowDiff(index=0, diffs=[FieldDiff("x", 1, 2)])
    assert rd.has_changes is True


def test_row_diff_has_changes_false_when_empty():
    rd = RowDiff(index=0)
    assert rd.has_changes is False


def test_row_diff_str_contains_index():
    rd = RowDiff(index=3, diffs=[FieldDiff("col", "a", "b")])
    assert "3" in str(rd)


# ---------------------------------------------------------------------------
# DiffReport
# ---------------------------------------------------------------------------

def test_diff_report_has_differences_with_changed_rows():
    rd = RowDiff(index=0, diffs=[FieldDiff("x", 1, 2)])
    report = DiffReport(table_name="users", row_diffs=[rd])
    assert report.has_differences is True


def test_diff_report_has_differences_with_only_in_left():
    report = DiffReport(table_name="users", only_in_left=[0])
    assert report.has_differences is True


def test_diff_report_no_differences_when_all_empty():
    rd = RowDiff(index=0, diffs=[])
    report = DiffReport(table_name="users", row_diffs=[rd])
    assert report.has_differences is False


def test_diff_report_summary_contains_table_name():
    report = DiffReport(table_name="orders")
    assert "orders" in report.summary()


# ---------------------------------------------------------------------------
# diff_row
# ---------------------------------------------------------------------------

def test_diff_row_identical_rows_no_diffs():
    row = {"id": 1, "name": "Alice"}
    result = diff_row(0, row, row.copy())
    assert not result.has_changes


def test_diff_row_detects_single_change():
    left = {"id": 1, "name": "Alice"}
    right = {"id": 1, "name": "Bob"}
    result = diff_row(0, left, right)
    assert result.has_changes
    assert result.diffs[0].column == "name"


def test_diff_row_respects_column_filter():
    left = {"id": 1, "name": "Alice", "age": 30}
    right = {"id": 2, "name": "Alice", "age": 31}
    result = diff_row(0, left, right, columns=["name"])
    assert not result.has_changes


def test_diff_row_missing_key_treated_as_none():
    left = {"id": 1}
    right = {"id": 1, "extra": "value"}
    result = diff_row(0, left, right)
    assert result.has_changes
    assert any(d.column == "extra" for d in result.diffs)


# ---------------------------------------------------------------------------
# diff_rows
# ---------------------------------------------------------------------------

def test_diff_rows_returns_diff_report():
    left = [{"id": 1}]
    right = [{"id": 1}]
    report = diff_rows("users", left, right)
    assert isinstance(report, DiffReport)


def test_diff_rows_detects_extra_left_rows():
    left = [{"id": 1}, {"id": 2}]
    right = [{"id": 1}]
    report = diff_rows("users", left, right)
    assert 1 in report.only_in_left


def test_diff_rows_detects_extra_right_rows():
    left = [{"id": 1}]
    right = [{"id": 1}, {"id": 2}]
    report = diff_rows("users", left, right)
    assert 1 in report.only_in_right


def test_diff_rows_table_name_preserved():
    report = diff_rows("products", [], [])
    assert report.table_name == "products"


def test_diff_rows_row_count_matches_min_length():
    left = [{"id": i} for i in range(5)]
    right = [{"id": i} for i in range(3)]
    report = diff_rows("t", left, right)
    assert len(report.row_diffs) == 3
