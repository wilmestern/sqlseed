"""Tests for sqlseed.row_filter."""

from __future__ import annotations

import pytest

from sqlseed.row_filter import RowFilter, filter_rows


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def sample_rows():
    return [
        {"id": 1, "age": 25, "active": True},
        {"id": 2, "age": 17, "active": False},
        {"id": 3, "age": 30, "active": True},
        {"id": 4, "age": 15, "active": True},
    ]


# ---------------------------------------------------------------------------
# RowFilter.add / names
# ---------------------------------------------------------------------------

def test_add_registers_predicate():
    rf = RowFilter()
    rf.add("is_adult", lambda r: r["age"] >= 18)
    assert "is_adult" in rf.names()


def test_names_returns_all_registered():
    rf = RowFilter()
    rf.add("a", lambda r: True)
    rf.add("b", lambda r: True)
    assert rf.names() == ["a", "b"]


# ---------------------------------------------------------------------------
# RowFilter.remove
# ---------------------------------------------------------------------------

def test_remove_existing_predicate():
    rf = RowFilter()
    rf.add("keep", lambda r: True)
    rf.add("drop", lambda r: False)
    rf.remove("drop")
    assert "drop" not in rf.names()
    assert "keep" in rf.names()


def test_remove_unknown_name_does_not_raise():
    rf = RowFilter()
    rf.remove("nonexistent")  # should not raise


# ---------------------------------------------------------------------------
# RowFilter.clear
# ---------------------------------------------------------------------------

def test_clear_removes_all_predicates():
    rf = RowFilter()
    rf.add("p1", lambda r: True)
    rf.add("p2", lambda r: True)
    rf.clear()
    assert rf.names() == []


# ---------------------------------------------------------------------------
# RowFilter.passes
# ---------------------------------------------------------------------------

def test_passes_no_predicates_always_true():
    rf = RowFilter()
    assert rf.passes({"id": 1}) is True


def test_passes_single_predicate_true():
    rf = RowFilter()
    rf.add("adult", lambda r: r["age"] >= 18)
    assert rf.passes({"age": 20}) is True


def test_passes_single_predicate_false():
    rf = RowFilter()
    rf.add("adult", lambda r: r["age"] >= 18)
    assert rf.passes({"age": 16}) is False


def test_passes_multiple_predicates_all_must_pass():
    rf = RowFilter()
    rf.add("adult", lambda r: r["age"] >= 18)
    rf.add("active", lambda r: r["active"] is True)
    assert rf.passes({"age": 25, "active": True}) is True
    assert rf.passes({"age": 25, "active": False}) is False
    assert rf.passes({"age": 16, "active": True}) is False


# ---------------------------------------------------------------------------
# RowFilter.apply
# ---------------------------------------------------------------------------

def test_apply_filters_rows(sample_rows):
    rf = RowFilter()
    rf.add("adult", lambda r: r["age"] >= 18)
    result = rf.apply(sample_rows)
    assert len(result) == 2
    assert all(r["age"] >= 18 for r in result)


def test_apply_empty_rows_returns_empty():
    rf = RowFilter()
    rf.add("p", lambda r: True)
    assert rf.apply([]) == []


# ---------------------------------------------------------------------------
# filter_rows helper
# ---------------------------------------------------------------------------

def test_filter_rows_with_no_predicates_returns_all(sample_rows):
    result = filter_rows(sample_rows, [])
    assert result == sample_rows


def test_filter_rows_single_predicate(sample_rows):
    result = filter_rows(sample_rows, [lambda r: r["active"]])
    assert all(r["active"] for r in result)
    assert len(result) == 3


def test_filter_rows_multiple_predicates(sample_rows):
    result = filter_rows(
        sample_rows,
        [lambda r: r["active"], lambda r: r["age"] >= 18],
    )
    assert len(result) == 2
