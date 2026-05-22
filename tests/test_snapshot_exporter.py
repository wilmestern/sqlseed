"""Tests for sqlseed.snapshot_exporter."""

from __future__ import annotations

import json

import pytest

from sqlseed.row_snapshot import Snapshot
from sqlseed.snapshot_exporter import (
    export_diff_json,
    export_snapshot,
    export_snapshot_csv,
    export_snapshot_json,
)


_ROWS = [
    {"id": 1, "name": "Alice"},
    {"id": 2, "name": "Bob"},
]


@pytest.fixture()
def snap() -> Snapshot:
    return Snapshot(name="test_snap", table="users", rows=_ROWS)


# ---------------------------------------------------------------------------
# export_snapshot_json
# ---------------------------------------------------------------------------

def test_export_snapshot_json_is_valid_json(snap):
    result = export_snapshot_json(snap)
    parsed = json.loads(result)
    assert isinstance(parsed, dict)


def test_export_snapshot_json_contains_name(snap):
    result = json.loads(export_snapshot_json(snap))
    assert result["name"] == "test_snap"


def test_export_snapshot_json_contains_rows(snap):
    result = json.loads(export_snapshot_json(snap))
    assert result["row_count"] == 2
    assert len(result["rows"]) == 2


def test_export_snapshot_json_contains_table(snap):
    result = json.loads(export_snapshot_json(snap))
    assert result["table"] == "users"


# ---------------------------------------------------------------------------
# export_snapshot_csv
# ---------------------------------------------------------------------------

def test_export_snapshot_csv_returns_string(snap):
    result = export_snapshot_csv(snap)
    assert isinstance(result, str)


def test_export_snapshot_csv_contains_header(snap):
    result = export_snapshot_csv(snap)
    assert "id" in result
    assert "name" in result


def test_export_snapshot_csv_empty_rows_returns_empty():
    empty = Snapshot(name="empty", table="users", rows=[])
    assert export_snapshot_csv(empty) == ""


# ---------------------------------------------------------------------------
# export_snapshot (dispatcher)
# ---------------------------------------------------------------------------

def test_export_snapshot_json_format(snap):
    result = export_snapshot(snap, fmt="json")
    json.loads(result)  # should not raise


def test_export_snapshot_csv_format(snap):
    result = export_snapshot(snap, fmt="csv")
    assert "Alice" in result


def test_export_snapshot_invalid_format_raises(snap):
    with pytest.raises(ValueError, match="Unsupported"):
        export_snapshot(snap, fmt="xml")


# ---------------------------------------------------------------------------
# export_diff_json
# ---------------------------------------------------------------------------

def test_export_diff_json_is_valid_json():
    a = Snapshot(name="a", table="users", rows=[{"id": 1}])
    b = Snapshot(name="b", table="users", rows=[{"id": 1}, {"id": 2}])
    result = json.loads(export_diff_json(a, b))
    assert result["added_count"] == 1


def test_export_diff_json_contains_snapshot_names():
    a = Snapshot(name="snap_a", table="users", rows=[])
    b = Snapshot(name="snap_b", table="users", rows=[])
    result = json.loads(export_diff_json(a, b))
    assert result["snapshot_a"] == "snap_a"
    assert result["snapshot_b"] == "snap_b"
