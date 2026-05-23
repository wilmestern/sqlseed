"""Tests for sqlseed.row_merger and sqlseed.merged_export."""
from __future__ import annotations

import pytest

from sqlseed.row_merger import MergeConfig, Row, merge_rows, merge_summary


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def left_rows() -> list[Row]:
    return [
        {"id": 1, "name": "Alice", "email": "alice@example.com"},
        {"id": 2, "name": "Bob", "email": "bob@example.com"},
    ]


@pytest.fixture()
def right_rows() -> list[Row]:
    return [
        {"id": 2, "name": "Bobby", "email": "bobby@example.com"},
        {"id": 3, "name": "Carol", "email": "carol@example.com"},
    ]


# ---------------------------------------------------------------------------
# MergeConfig
# ---------------------------------------------------------------------------


def test_merge_config_normalises_key_columns_lowercase() -> None:
    cfg = MergeConfig(key_columns=["ID", "Name"])
    assert cfg.key_columns == ["id", "name"]


def test_merge_config_case_sensitive_preserves_case() -> None:
    cfg = MergeConfig(key_columns=["ID"], case_sensitive_keys=True)
    assert cfg.key_columns == ["ID"]


def test_merge_config_invalid_prefer_raises() -> None:
    with pytest.raises(ValueError, match="prefer"):
        MergeConfig(key_columns=["id"], prefer="both")


def test_merge_config_empty_key_columns_raises() -> None:
    with pytest.raises(ValueError, match="key_columns"):
        MergeConfig(key_columns=[])


# ---------------------------------------------------------------------------
# merge_rows
# ---------------------------------------------------------------------------


def test_merge_rows_length(left_rows, right_rows) -> None:
    cfg = MergeConfig(key_columns=["id"])
    result = merge_rows(left_rows, right_rows, cfg)
    # id=1 (left only), id=2 (both), id=3 (right only) → 3 rows
    assert len(result) == 3


def test_merge_rows_right_wins_by_default(left_rows, right_rows) -> None:
    cfg = MergeConfig(key_columns=["id"], prefer="right")
    result = merge_rows(left_rows, right_rows, cfg)
    row2 = next(r for r in result if r["id"] == 2)
    assert row2["name"] == "Bobby"


def test_merge_rows_left_wins_when_prefer_left(left_rows, right_rows) -> None:
    cfg = MergeConfig(key_columns=["id"], prefer="left")
    result = merge_rows(left_rows, right_rows, cfg)
    row2 = next(r for r in result if r["id"] == 2)
    assert row2["name"] == "Bob"


def test_merge_rows_includes_left_only_row(left_rows, right_rows) -> None:
    cfg = MergeConfig(key_columns=["id"])
    result = merge_rows(left_rows, right_rows, cfg)
    ids = [r["id"] for r in result]
    assert 1 in ids


def test_merge_rows_includes_right_only_row(left_rows, right_rows) -> None:
    cfg = MergeConfig(key_columns=["id"])
    result = merge_rows(left_rows, right_rows, cfg)
    ids = [r["id"] for r in result]
    assert 3 in ids


def test_merge_rows_empty_left(right_rows) -> None:
    cfg = MergeConfig(key_columns=["id"])
    result = merge_rows([], right_rows, cfg)
    assert len(result) == len(right_rows)


def test_merge_rows_empty_right(left_rows) -> None:
    cfg = MergeConfig(key_columns=["id"])
    result = merge_rows(left_rows, [], cfg)
    assert len(result) == len(left_rows)


# ---------------------------------------------------------------------------
# merge_summary
# ---------------------------------------------------------------------------


def test_merge_summary_before_count(left_rows, right_rows) -> None:
    cfg = MergeConfig(key_columns=["id"])
    merged = merge_rows(left_rows, right_rows, cfg)
    summary = merge_summary(left_rows, merged)
    assert summary["before"] == 2


def test_merge_summary_after_count(left_rows, right_rows) -> None:
    cfg = MergeConfig(key_columns=["id"])
    merged = merge_rows(left_rows, right_rows, cfg)
    summary = merge_summary(left_rows, merged)
    assert summary["after"] == 3


def test_merge_summary_added_count(left_rows, right_rows) -> None:
    cfg = MergeConfig(key_columns=["id"])
    merged = merge_rows(left_rows, right_rows, cfg)
    summary = merge_summary(left_rows, merged)
    assert summary["added"] == 1
