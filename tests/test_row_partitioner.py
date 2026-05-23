"""Tests for sqlseed.row_partitioner."""

from __future__ import annotations

import pytest

from sqlseed.row_partitioner import (
    PartitionConfig,
    PartitionResult,
    partition_rows,
    partition_sizes,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def sample_rows():
    return [
        {"id": 1, "age": 17, "active": True},
        {"id": 2, "age": 25, "active": True},
        {"id": 3, "age": 30, "active": False},
        {"id": 4, "age": 15, "active": False},
        {"id": 5, "age": 40, "active": True},
    ]


@pytest.fixture()
def age_rules():
    return [
        ("minor", lambda r: r["age"] < 18),
        ("adult", lambda r: r["age"] >= 18),
    ]


# ---------------------------------------------------------------------------
# PartitionConfig
# ---------------------------------------------------------------------------

def test_partition_config_default_partition_name():
    cfg = PartitionConfig()
    assert cfg.default_partition == "__other__"


def test_partition_config_custom_default_partition():
    cfg = PartitionConfig(default_partition="uncategorised")
    assert cfg.default_partition == "uncategorised"


def test_partition_config_empty_default_raises():
    with pytest.raises(ValueError):
        PartitionConfig(default_partition="")


def test_partition_config_whitespace_default_raises():
    with pytest.raises(ValueError):
        PartitionConfig(default_partition="   ")


# ---------------------------------------------------------------------------
# partition_rows
# ---------------------------------------------------------------------------

def test_partition_rows_returns_partition_result(sample_rows, age_rules):
    result = partition_rows(sample_rows, age_rules)
    assert isinstance(result, PartitionResult)


def test_partition_rows_correct_bucket_names(sample_rows, age_rules):
    result = partition_rows(sample_rows, age_rules)
    assert set(result.names()) == {"minor", "adult"}


def test_partition_rows_minor_count(sample_rows, age_rules):
    result = partition_rows(sample_rows, age_rules)
    assert len(result.get("minor")) == 2


def test_partition_rows_adult_count(sample_rows, age_rules):
    result = partition_rows(sample_rows, age_rules)
    assert len(result.get("adult")) == 3


def test_partition_rows_total_equals_input(sample_rows, age_rules):
    result = partition_rows(sample_rows, age_rules)
    assert result.total() == len(sample_rows)


def test_partition_rows_unmatched_goes_to_default(sample_rows):
    rules = [("active", lambda r: r["active"] is True)]
    result = partition_rows(sample_rows, rules)
    assert len(result.get("__other__")) == 2


def test_partition_rows_empty_input_returns_empty_result(age_rules):
    result = partition_rows([], age_rules)
    assert result.total() == 0


def test_partition_rows_no_rules_all_in_default(sample_rows):
    result = partition_rows(sample_rows, [])
    assert result.total() == len(sample_rows)
    assert "__other__" in result.names()


def test_partition_rows_first_matching_rule_wins():
    rows = [{"score": 50}]
    rules = [
        ("low", lambda r: r["score"] < 100),
        ("medium", lambda r: r["score"] < 100),
    ]
    result = partition_rows(rows, rules)
    assert len(result.get("low")) == 1
    assert len(result.get("medium")) == 0


# ---------------------------------------------------------------------------
# partition_sizes
# ---------------------------------------------------------------------------

def test_partition_sizes_returns_dict(sample_rows, age_rules):
    result = partition_rows(sample_rows, age_rules)
    sizes = partition_sizes(result)
    assert isinstance(sizes, dict)


def test_partition_sizes_values_match_bucket_lengths(sample_rows, age_rules):
    result = partition_rows(sample_rows, age_rules)
    sizes = partition_sizes(result)
    for name, count in sizes.items():
        assert count == len(result.get(name))


# ---------------------------------------------------------------------------
# PartitionResult helpers
# ---------------------------------------------------------------------------

def test_partition_result_get_missing_returns_empty_list(sample_rows, age_rules):
    result = partition_rows(sample_rows, age_rules)
    assert result.get("nonexistent") == []


def test_partition_result_names_are_sorted():
    result = PartitionResult(buckets={"z": [], "a": [], "m": []})
    assert result.names() == ["a", "m", "z"]
