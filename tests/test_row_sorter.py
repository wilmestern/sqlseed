"""Tests for sqlseed.row_sorter."""

import pytest

from sqlseed.row_sorter import RowSorter, SortKey, sort_rows


@pytest.fixture()
def sorter() -> RowSorter:
    return RowSorter()


@pytest.fixture()
def sample_rows():
    return [
        {"id": 3, "name": "Charlie", "age": 25},
        {"id": 1, "name": "Alice", "age": 30},
        {"id": 2, "name": "Bob", "age": 25},
    ]


# --- SortKey ---

def test_sort_key_empty_column_raises():
    with pytest.raises(ValueError, match="empty"):
        SortKey(column="   ")


def test_sort_key_strips_whitespace():
    sk = SortKey(column="  name  ")
    assert sk.column == "name"


# --- RowSorter.add / columns ---

def test_add_registers_column(sorter):
    sorter.add("id")
    assert "id" in sorter.columns


def test_columns_preserves_order(sorter):
    sorter.add("age")
    sorter.add("name")
    assert sorter.columns == ["age", "name"]


# --- RowSorter.remove ---

def test_remove_existing_key(sorter):
    sorter.add("id")
    sorter.remove("id")
    assert "id" not in sorter.columns


def test_remove_unknown_column_does_not_raise(sorter):
    sorter.remove("nonexistent")  # should not raise


def test_remove_is_case_insensitive(sorter):
    sorter.add("Name")
    sorter.remove("name")
    assert sorter.columns == []


# --- RowSorter.clear ---

def test_clear_removes_all_keys(sorter):
    sorter.add("id")
    sorter.add("name")
    sorter.clear()
    assert sorter.columns == []


# --- RowSorter.sort ---

def test_sort_ascending_by_id(sorter, sample_rows):
    sorter.add("id", ascending=True)
    result = sorter.sort(sample_rows)
    assert [r["id"] for r in result] == [1, 2, 3]


def test_sort_descending_by_id(sorter, sample_rows):
    sorter.add("id", ascending=False)
    result = sorter.sort(sample_rows)
    assert [r["id"] for r in result] == [3, 2, 1]


def test_sort_by_name_ascending(sorter, sample_rows):
    sorter.add("name", ascending=True)
    result = sorter.sort(sample_rows)
    assert [r["name"] for r in result] == ["Alice", "Bob", "Charlie"]


def test_sort_empty_rows_returns_empty(sorter):
    assert sorter.sort([]) == []


def test_sort_no_keys_returns_copy(sorter, sample_rows):
    result = sorter.sort(sample_rows)
    assert result == sample_rows
    assert result is not sample_rows


def test_sort_does_not_mutate_original(sorter, sample_rows):
    original_order = [r["id"] for r in sample_rows]
    sorter.add("id")
    sorter.sort(sample_rows)
    assert [r["id"] for r in sample_rows] == original_order


def test_sort_none_values_pushed_to_end(sorter):
    rows = [{"id": 2}, {"id": None}, {"id": 1}]
    sorter.add("id", ascending=True)
    result = sorter.sort(rows)
    assert result[-1]["id"] is None


def test_sort_with_custom_key_fn(sorter, sample_rows):
    # Sort by lowercase name length
    sorter.add("name", ascending=True, key_fn=len)
    result = sorter.sort(sample_rows)
    # Alice(5), Charlie(7), Bob(3) -> Bob, Alice, Charlie
    assert result[0]["name"] == "Bob"


def test_multi_key_sort_age_then_name(sorter, sample_rows):
    sorter.add("age", ascending=True)
    sorter.add("name", ascending=True)
    result = sorter.sort(sample_rows)
    # age 25: Bob, Charlie; age 30: Alice
    assert result[0]["age"] == 25
    assert result[-1]["name"] == "Alice"


# --- sort_rows convenience function ---

def test_sort_rows_convenience(sample_rows):
    result = sort_rows(sample_rows, "id", ascending=True)
    assert [r["id"] for r in result] == [1, 2, 3]


def test_sort_rows_descending(sample_rows):
    result = sort_rows(sample_rows, "name", ascending=False)
    assert result[0]["name"] == "Charlie"
