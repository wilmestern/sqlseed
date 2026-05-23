"""Tests for sqlseed.row_grouper."""

import pytest

from sqlseed.row_grouper import (
    GrouperConfig,
    _make_key,
    filter_group,
    group_rows,
    group_sizes,
    largest_group,
)


@pytest.fixture()
def sample_rows():
    return [
        {"id": 1, "status": "active", "country": "US"},
        {"id": 2, "status": "inactive", "country": "US"},
        {"id": 3, "status": "active", "country": "UK"},
        {"id": 4, "status": "active", "country": "US"},
        {"id": 5, "status": "inactive", "country": "UK"},
    ]


def test_grouper_config_normalises_columns_lowercase():
    cfg = GrouperConfig(key_columns=["Status", "COUNTRY"])
    assert cfg.key_columns == ["status", "country"]


def test_grouper_config_empty_columns_raises():
    with pytest.raises(ValueError, match="key_columns"):
        GrouperConfig(key_columns=[])


def test_grouper_config_case_sensitive_preserves_case():
    cfg = GrouperConfig(key_columns=["Status"], case_sensitive=True)
    assert cfg.key_columns == ["Status"]


def test_group_rows_correct_number_of_groups(sample_rows):
    cfg = GrouperConfig(key_columns=["status"])
    groups = group_rows(sample_rows, cfg)
    assert len(groups) == 2


def test_group_rows_keys_are_tuples(sample_rows):
    cfg = GrouperConfig(key_columns=["status"])
    groups = group_rows(sample_rows, cfg)
    for key in groups:
        assert isinstance(key, tuple)


def test_group_rows_correct_row_counts(sample_rows):
    cfg = GrouperConfig(key_columns=["status"])
    groups = group_rows(sample_rows, cfg)
    assert len(groups[("active",)]) == 3
    assert len(groups[("inactive",)]) == 2


def test_group_rows_multi_column_key(sample_rows):
    cfg = GrouperConfig(key_columns=["status", "country"])
    groups = group_rows(sample_rows, cfg)
    assert ("active", "US") in groups
    assert len(groups[("active", "US")]) == 2


def test_group_rows_empty_input():
    cfg = GrouperConfig(key_columns=["status"])
    groups = group_rows([], cfg)
    assert groups == {}


def test_group_sizes_returns_correct_counts(sample_rows):
    cfg = GrouperConfig(key_columns=["status"])
    groups = group_rows(sample_rows, cfg)
    sizes = group_sizes(groups)
    assert sizes[("active",)] == 3
    assert sizes[("inactive",)] == 2


def test_largest_group_returns_biggest(sample_rows):
    cfg = GrouperConfig(key_columns=["status"])
    groups = group_rows(sample_rows, cfg)
    key, rows = largest_group(groups)
    assert key == ("active",)
    assert len(rows) == 3


def test_largest_group_empty_returns_none():
    assert largest_group({}) is None


def test_filter_group_returns_rows(sample_rows):
    cfg = GrouperConfig(key_columns=["status"])
    groups = group_rows(sample_rows, cfg)
    rows = filter_group(groups, ("active",))
    assert len(rows) == 3


def test_filter_group_missing_key_returns_empty(sample_rows):
    cfg = GrouperConfig(key_columns=["status"])
    groups = group_rows(sample_rows, cfg)
    rows = filter_group(groups, ("unknown",))
    assert rows == []


def test_make_key_case_insensitive_column_lookup():
    row = {"Status": "active", "Country": "US"}
    key = _make_key(row, ["status", "country"], case_sensitive=False)
    assert key == ("active", "US")
