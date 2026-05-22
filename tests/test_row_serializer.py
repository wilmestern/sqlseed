"""Tests for sqlseed.row_serializer."""

from __future__ import annotations

import json

import pytest

from sqlseed.row_serializer import (
    serialize_rows,
    serialize_rows_csv,
    serialize_rows_json,
)
from sqlseed.schema_parser import ColumnDefinition, TableDefinition


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def simple_table() -> TableDefinition:
    return TableDefinition(
        name="users",
        columns=[
            ColumnDefinition(name="id", col_type="INTEGER", nullable=False, primary_key=True),
            ColumnDefinition(name="email", col_type="VARCHAR", nullable=False, primary_key=False),
            ColumnDefinition(name="score", col_type="FLOAT", nullable=True, primary_key=False),
        ],
    )


@pytest.fixture()
def sample_rows():
    return [
        {"id": 1, "email": "alice@example.com", "score": 9.5},
        {"id": 2, "email": "bob@example.com", "score": None},
    ]


# ---------------------------------------------------------------------------
# JSON serialisation
# ---------------------------------------------------------------------------


def test_serialize_rows_json_returns_valid_json(sample_rows):
    result = serialize_rows_json(sample_rows)
    parsed = json.loads(result)
    assert isinstance(parsed, list)


def test_serialize_rows_json_length(sample_rows):
    parsed = json.loads(serialize_rows_json(sample_rows))
    assert len(parsed) == 2


def test_serialize_rows_json_none_preserved(sample_rows):
    parsed = json.loads(serialize_rows_json(sample_rows))
    assert parsed[1]["score"] is None


def test_serialize_rows_json_values(sample_rows):
    parsed = json.loads(serialize_rows_json(sample_rows))
    assert parsed[0]["email"] == "alice@example.com"


# ---------------------------------------------------------------------------
# CSV serialisation
# ---------------------------------------------------------------------------


def test_serialize_rows_csv_has_header(sample_rows, simple_table):
    result = serialize_rows_csv(sample_rows, simple_table)
    first_line = result.splitlines()[0]
    assert "id" in first_line and "email" in first_line


def test_serialize_rows_csv_row_count(sample_rows, simple_table):
    lines = serialize_rows_csv(sample_rows, simple_table).strip().splitlines()
    # header + 2 data rows
    assert len(lines) == 3


def test_serialize_rows_csv_none_becomes_empty(sample_rows, simple_table):
    result = serialize_rows_csv(sample_rows, simple_table)
    data_lines = result.strip().splitlines()[1:]
    # second row has None score → empty field at end
    assert data_lines[1].endswith(",")


def test_serialize_rows_csv_empty_rows(simple_table):
    result = serialize_rows_csv([], simple_table)
    assert result == ""


# ---------------------------------------------------------------------------
# TSV serialisation
# ---------------------------------------------------------------------------


def test_serialize_rows_tsv_uses_tab(sample_rows, simple_table):
    result = serialize_rows(sample_rows, simple_table, fmt="tsv")
    assert "\t" in result


# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------


def test_serialize_rows_json_dispatch(sample_rows, simple_table):
    result = serialize_rows(sample_rows, simple_table, fmt="json")
    assert result.startswith("[")


def test_serialize_rows_csv_dispatch(sample_rows, simple_table):
    result = serialize_rows(sample_rows, simple_table, fmt="csv")
    assert "email" in result


def test_serialize_rows_invalid_format_raises(sample_rows, simple_table):
    with pytest.raises(ValueError, match="Unsupported"):
        serialize_rows(sample_rows, simple_table, fmt="xml")  # type: ignore[arg-type]
