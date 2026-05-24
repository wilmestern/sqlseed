"""Tests for sqlseed.row_splitter."""

import pytest

from sqlseed.row_splitter import (
    SplitResult,
    SplitterConfig,
    SplitterError,
    split_rows,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def sample_rows():
    return [
        {"id": 1, "status": "active", "score": 90},
        {"id": 2, "status": "inactive", "score": 40},
        {"id": 3, "status": "active", "score": 55},
        {"id": 4, "status": "pending", "score": 70},
        {"id": 5, "status": "inactive", "score": 20},
    ]


@pytest.fixture()
def status_rules():
    return [
        ("active", lambda row: row["status"] == "active"),
        ("inactive", lambda row: row["status"] == "inactive"),
    ]


# ---------------------------------------------------------------------------
# SplitterConfig tests
# ---------------------------------------------------------------------------


def test_splitter_config_default_bucket():
    cfg = SplitterConfig()
    assert cfg.default_bucket == "other"


def test_splitter_config_custom_default_bucket():
    cfg = SplitterConfig(default_bucket="unmatched")
    assert cfg.default_bucket == "unmatched"


def test_splitter_config_empty_default_bucket_raises():
    with pytest.raises(SplitterError):
        SplitterConfig(default_bucket="")


def test_splitter_config_whitespace_default_bucket_raises():
    with pytest.raises(SplitterError):
        SplitterConfig(default_bucket="   ")


def test_splitter_config_strips_whitespace():
    cfg = SplitterConfig(default_bucket="  rest  ")
    assert cfg.default_bucket == "rest"


# ---------------------------------------------------------------------------
# split_rows tests
# ---------------------------------------------------------------------------


def test_split_rows_returns_split_result(sample_rows, status_rules):
    result = split_rows(sample_rows, status_rules)
    assert isinstance(result, SplitResult)


def test_split_rows_active_bucket_count(sample_rows, status_rules):
    result = split_rows(sample_rows, status_rules)
    assert len(result.get("active")) == 2


def test_split_rows_inactive_bucket_count(sample_rows, status_rules):
    result = split_rows(sample_rows, status_rules)
    assert len(result.get("inactive")) == 2


def test_split_rows_unmatched_goes_to_default(sample_rows, status_rules):
    result = split_rows(sample_rows, status_rules)
    assert len(result.get("other")) == 1
    assert result.get("other")[0]["status"] == "pending"


def test_split_rows_total_equals_input(sample_rows, status_rules):
    result = split_rows(sample_rows, status_rules)
    assert result.total() == len(sample_rows)


def test_split_rows_names_returns_non_empty_buckets(sample_rows, status_rules):
    result = split_rows(sample_rows, status_rules)
    assert set(result.names()) == {"active", "inactive", "other"}


def test_split_rows_empty_input_returns_empty_result(status_rules):
    result = split_rows([], status_rules)
    assert result.total() == 0
    assert result.names() == []


def test_split_rows_no_rules_all_go_to_default(sample_rows):
    result = split_rows(sample_rows, [])
    assert result.get("other") == sample_rows


def test_split_rows_custom_default_bucket(sample_rows, status_rules):
    cfg = SplitterConfig(default_bucket="remainder")
    result = split_rows(sample_rows, status_rules, config=cfg)
    assert len(result.get("remainder")) == 1


def test_split_rows_first_matching_rule_wins():
    rows = [{"val": 5}]
    rules = [
        ("low", lambda r: r["val"] < 10),
        ("also_low", lambda r: r["val"] < 10),
    ]
    result = split_rows(rows, rules)
    assert len(result.get("low")) == 1
    assert len(result.get("also_low")) == 0


def test_split_rows_predicate_exception_raises_splitter_error():
    rows = [{"val": 1}]
    bad_rules = [("boom", lambda r: 1 / 0)]
    with pytest.raises(SplitterError, match="boom"):
        split_rows(rows, bad_rules)
