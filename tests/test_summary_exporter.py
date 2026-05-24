"""Tests for sqlseed.summary_exporter."""

from __future__ import annotations

import json

import pytest

from sqlseed.row_summarizer import summarize_rows
from sqlseed.summary_exporter import (
    export_summary,
    export_summary_json,
    export_summary_text,
    summarize_table,
)
from sqlseed.schema_parser import TableDefinition, ColumnDefinition


@pytest.fixture()
def summary():
    rows = [
        {"id": 1, "username": "alice", "email": "alice@example.com"},
        {"id": 2, "username": "bob", "email": None},
        {"id": 3, "username": "carol", "email": "carol@example.com"},
    ]
    return summarize_rows("users", rows)


@pytest.fixture()
def simple_table():
    return TableDefinition(
        name="users",
        columns=[
            ColumnDefinition(name="id", col_type="INTEGER", nullable=False, is_primary_key=True),
            ColumnDefinition(name="username", col_type="VARCHAR", nullable=False, max_length=50),
        ],
    )


def test_export_summary_json_returns_string(summary):
    result = export_summary_json(summary)
    assert isinstance(result, str)


def test_export_summary_json_is_valid_json(summary):
    result = export_summary_json(summary)
    parsed = json.loads(result)
    assert isinstance(parsed, dict)


def test_export_summary_json_contains_table(summary):
    parsed = json.loads(export_summary_json(summary))
    assert parsed["table"] == "users"


def test_export_summary_json_contains_row_count(summary):
    parsed = json.loads(export_summary_json(summary))
    assert parsed["row_count"] == 3


def test_export_summary_json_contains_columns(summary):
    parsed = json.loads(export_summary_json(summary))
    assert "columns" in parsed
    assert "email" in parsed["columns"]


def test_export_summary_text_returns_string(summary):
    result = export_summary_text(summary)
    assert isinstance(result, str)


def test_export_summary_text_contains_table_name(summary):
    result = export_summary_text(summary)
    assert "users" in result


def test_export_summary_text_contains_column_name(summary):
    result = export_summary_text(summary)
    assert "email" in result


def test_export_summary_dispatch_json(summary):
    result = export_summary(summary, fmt="json")
    assert json.loads(result)["table"] == "users"


def test_export_summary_dispatch_text(summary):
    result = export_summary(summary, fmt="text")
    assert "users" in result


def test_export_summary_dispatch_txt_alias(summary):
    result = export_summary(summary, fmt="txt")
    assert "users" in result


def test_export_summary_invalid_format_raises(summary):
    with pytest.raises(ValueError, match="Unsupported summary format"):
        export_summary(summary, fmt="xml")


def test_summarize_table_returns_row_summary(simple_table):
    result = summarize_table(simple_table, count=5)
    assert result.row_count == 5
    assert result.table == "users"


def test_summarize_table_zero_count(simple_table):
    result = summarize_table(simple_table, count=0)
    assert result.row_count == 0
