"""Tests for sqlseed.partitioned_export."""

from __future__ import annotations

import json

import pytest

from sqlseed.partitioned_export import (
    export_all_partitions_as_json,
    export_partition_as_json,
    generate_and_partition,
    largest_partition,
)
from sqlseed.row_partitioner import PartitionResult, partition_rows
from sqlseed.schema_parser import ColumnDefinition, TableDefinition


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _simple_table() -> TableDefinition:
    return TableDefinition(
        name="users",
        columns=[
            ColumnDefinition(name="id", data_type="INTEGER", nullable=False, primary_key=True),
            ColumnDefinition(name="score", data_type="INTEGER", nullable=True),
        ],
    )


@pytest.fixture()
def pre_built_result():
    rows = [
        {"id": 1, "score": 10},
        {"id": 2, "score": 90},
        {"id": 3, "score": 55},
    ]
    rules = [
        ("low", lambda r: (r["score"] or 0) < 50),
        ("high", lambda r: (r["score"] or 0) >= 50),
    ]
    return partition_rows(rows, rules)


# ---------------------------------------------------------------------------
# generate_and_partition
# ---------------------------------------------------------------------------

def test_generate_and_partition_returns_partition_result():
    table = _simple_table()
    rules = [("all", lambda r: True)]
    result = generate_and_partition(table, 5, rules)
    assert isinstance(result, PartitionResult)


def test_generate_and_partition_total_equals_count():
    table = _simple_table()
    rules = [("all", lambda r: True)]
    result = generate_and_partition(table, 8, rules)
    assert result.total() == 8


# ---------------------------------------------------------------------------
# export_partition_as_json
# ---------------------------------------------------------------------------

def test_export_partition_as_json_is_valid_json(pre_built_result):
    output = export_partition_as_json(pre_built_result, "low")
    parsed = json.loads(output)
    assert isinstance(parsed, list)


def test_export_partition_as_json_correct_count(pre_built_result):
    output = export_partition_as_json(pre_built_result, "low")
    parsed = json.loads(output)
    assert len(parsed) == len(pre_built_result.get("low"))


def test_export_partition_as_json_missing_bucket_returns_empty_array(pre_built_result):
    output = export_partition_as_json(pre_built_result, "nonexistent")
    assert json.loads(output) == []


# ---------------------------------------------------------------------------
# export_all_partitions_as_json
# ---------------------------------------------------------------------------

def test_export_all_partitions_as_json_is_valid_json(pre_built_result):
    output = export_all_partitions_as_json(pre_built_result)
    parsed = json.loads(output)
    assert isinstance(parsed, dict)


def test_export_all_partitions_as_json_contains_all_buckets(pre_built_result):
    output = export_all_partitions_as_json(pre_built_result)
    parsed = json.loads(output)
    assert set(parsed.keys()) == set(pre_built_result.names())


def test_export_all_partitions_as_json_sizes_match(pre_built_result):
    output = export_all_partitions_as_json(pre_built_result)
    parsed = json.loads(output)
    for name in pre_built_result.names():
        assert len(parsed[name]) == len(pre_built_result.get(name))


# ---------------------------------------------------------------------------
# largest_partition
# ---------------------------------------------------------------------------

def test_largest_partition_returns_string(pre_built_result):
    name = largest_partition(pre_built_result)
    assert isinstance(name, str)


def test_largest_partition_is_valid_bucket(pre_built_result):
    name = largest_partition(pre_built_result)
    assert name in pre_built_result.names()


def test_largest_partition_empty_result_raises():
    empty = PartitionResult(buckets={})
    with pytest.raises(ValueError):
        largest_partition(empty)
