"""Tests for sqlseed.row_truncator and sqlseed.truncated_export."""

from __future__ import annotations

import pytest

from sqlseed.row_truncator import (
    TruncatorConfig,
    TruncatorError,
    truncate_row,
    truncate_rows,
    truncate_value,
)
from sqlseed.schema_parser import ColumnDefinition, TableDefinition
from sqlseed.truncated_export import export_truncated, generate_truncated_rows


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _simple_table() -> TableDefinition:
    return TableDefinition(
        name="articles",
        columns=[
            ColumnDefinition(name="id", col_type="INTEGER", nullable=False, primary_key=True),
            ColumnDefinition(name="title", col_type="VARCHAR", nullable=False, max_length=200),
            ColumnDefinition(name="body", col_type="TEXT", nullable=True),
        ],
    )


# ---------------------------------------------------------------------------
# TruncatorConfig
# ---------------------------------------------------------------------------

def test_truncator_config_defaults():
    cfg = TruncatorConfig()
    assert cfg.global_max_length is None
    assert cfg.column_limits == {}
    assert cfg.ellipsis == ""


def test_truncator_config_invalid_global_max_raises():
    with pytest.raises(TruncatorError):
        TruncatorConfig(global_max_length=0)


def test_truncator_config_negative_global_max_raises():
    with pytest.raises(TruncatorError):
        TruncatorConfig(global_max_length=-5)


def test_truncator_config_invalid_column_limit_raises():
    with pytest.raises(TruncatorError):
        TruncatorConfig(column_limits={"title": 0})


def test_truncator_config_normalises_column_keys_lowercase():
    cfg = TruncatorConfig(column_limits={"Title": 50, "BODY": 100})
    assert "title" in cfg.column_limits
    assert "body" in cfg.column_limits


def test_add_column_limit_registers():
    cfg = TruncatorConfig()
    cfg.add_column_limit("title", 80)
    assert cfg.limit_for("title") == 80


def test_add_column_limit_empty_name_raises():
    cfg = TruncatorConfig()
    with pytest.raises(TruncatorError):
        cfg.add_column_limit("", 50)


def test_add_column_limit_zero_raises():
    cfg = TruncatorConfig()
    with pytest.raises(TruncatorError):
        cfg.add_column_limit("title", 0)


def test_remove_column_limit_removes_entry():
    cfg = TruncatorConfig(column_limits={"title": 50})
    cfg.remove_column_limit("title")
    assert cfg.limit_for("title") is None


def test_remove_unknown_column_limit_does_not_raise():
    cfg = TruncatorConfig()
    cfg.remove_column_limit("nonexistent")  # should not raise


def test_limit_for_column_overrides_global():
    cfg = TruncatorConfig(global_max_length=100, column_limits={"title": 20})
    assert cfg.limit_for("title") == 20
    assert cfg.limit_for("body") == 100


# ---------------------------------------------------------------------------
# truncate_value
# ---------------------------------------------------------------------------

def test_truncate_value_short_string_unchanged():
    assert truncate_value("hello", 10) == "hello"


def test_truncate_value_long_string_trimmed():
    result = truncate_value("abcdefgh", 4)
    assert result == "abcd"
    assert len(result) == 4


def test_truncate_value_with_ellipsis():
    result = truncate_value("abcdefgh", 5, "...")
    assert result.endswith("...")
    assert len(result) == 5


def test_truncate_value_non_string_unchanged():
    assert truncate_value(42, 3) == 42
    assert truncate_value(None, 3) is None


# ---------------------------------------------------------------------------
# truncate_row / truncate_rows
# ---------------------------------------------------------------------------

def test_truncate_row_applies_limit():
    cfg = TruncatorConfig(column_limits={"title": 5})
    row = {"id": 1, "title": "A very long title", "body": "Some body text"}
    result = truncate_row(row, cfg)
    assert len(result["title"]) == 5
    assert result["body"] == "Some body text"  # no limit on body


def test_truncate_row_global_limit():
    cfg = TruncatorConfig(global_max_length=8)
    row = {"title": "Hello World", "body": "Hi"}
    result = truncate_row(row, cfg)
    assert len(result["title"]) == 8
    assert result["body"] == "Hi"


def test_truncate_rows_returns_correct_count():
    cfg = TruncatorConfig(global_max_length=10)
    rows = [{"title": "x" * 20}] * 5
    result = truncate_rows(rows, cfg)
    assert len(result) == 5


# ---------------------------------------------------------------------------
# generate_truncated_rows / export_truncated
# ---------------------------------------------------------------------------

def test_generate_truncated_rows_returns_list():
    table = _simple_table()
    cfg = TruncatorConfig(global_max_length=50)
    result = generate_truncated_rows(table, 3, cfg)
    assert isinstance(result, list)
    assert len(result) == 3


def test_generate_truncated_rows_negative_count_raises():
    table = _simple_table()
    cfg = TruncatorConfig()
    with pytest.raises(ValueError):
        generate_truncated_rows(table, -1, cfg)


def test_export_truncated_respects_column_limit():
    table = _simple_table()
    rows = export_truncated(table, 10, column_limits={"title": 10})
    for row in rows:
        if isinstance(row.get("title"), str):
            assert len(row["title"]) <= 10


def test_export_truncated_zero_count_returns_empty():
    table = _simple_table()
    result = export_truncated(table, 0)
    assert result == []
