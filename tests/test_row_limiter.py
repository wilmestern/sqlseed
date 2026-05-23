"""Tests for sqlseed.row_limiter and sqlseed.limited_export."""

from __future__ import annotations

import pytest

from sqlseed.row_limiter import LimiterConfig, apply_limit, iter_limited_rows, limit_rows
from sqlseed.limited_export import export_limited, generate_limited_rows
from sqlseed.schema_parser import ColumnDefinition, TableDefinition


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def rows() -> list[dict]:
    return [{"id": i, "name": f"user_{i}"} for i in range(10)]


@pytest.fixture()
def simple_table() -> TableDefinition:
    cols = [
        ColumnDefinition(name="id", data_type="INTEGER", nullable=False, primary_key=True),
        ColumnDefinition(name="username", data_type="VARCHAR", nullable=False, max_length=50),
    ]
    return TableDefinition(name="users", columns=cols)


# ---------------------------------------------------------------------------
# LimiterConfig validation
# ---------------------------------------------------------------------------


def test_limiter_config_defaults() -> None:
    cfg = LimiterConfig()
    assert cfg.limit is None
    assert cfg.offset == 0
    assert cfg.window is None


def test_limiter_config_negative_limit_raises() -> None:
    with pytest.raises(ValueError, match="limit"):
        LimiterConfig(limit=-1)


def test_limiter_config_negative_offset_raises() -> None:
    with pytest.raises(ValueError, match="offset"):
        LimiterConfig(offset=-3)


def test_limiter_config_invalid_window_equal_bounds_raises() -> None:
    with pytest.raises(ValueError, match="window start"):
        LimiterConfig(window=(5, 5))


def test_limiter_config_invalid_window_start_greater_raises() -> None:
    with pytest.raises(ValueError, match="window start"):
        LimiterConfig(window=(8, 3))


def test_limiter_config_negative_window_bound_raises() -> None:
    with pytest.raises(ValueError, match="non-negative"):
        LimiterConfig(window=(-1, 5))


# ---------------------------------------------------------------------------
# limit_rows
# ---------------------------------------------------------------------------


def test_limit_rows_no_constraints_returns_all(rows: list[dict]) -> None:
    result = limit_rows(rows, LimiterConfig())
    assert result == rows


def test_limit_rows_applies_limit(rows: list[dict]) -> None:
    result = limit_rows(rows, LimiterConfig(limit=3))
    assert len(result) == 3


def test_limit_rows_applies_offset(rows: list[dict]) -> None:
    result = limit_rows(rows, LimiterConfig(offset=4))
    assert result[0]["id"] == 4


def test_limit_rows_offset_and_limit(rows: list[dict]) -> None:
    result = limit_rows(rows, LimiterConfig(offset=2, limit=3))
    assert [r["id"] for r in result] == [2, 3, 4]


def test_limit_rows_window_overrides_offset_limit(rows: list[dict]) -> None:
    result = limit_rows(rows, LimiterConfig(offset=0, limit=10, window=(3, 6)))
    assert [r["id"] for r in result] == [3, 4, 5]


def test_limit_rows_limit_zero_returns_empty(rows: list[dict]) -> None:
    result = limit_rows(rows, LimiterConfig(limit=0))
    assert result == []


def test_iter_limited_rows_yields_correct_items(rows: list[dict]) -> None:
    result = list(iter_limited_rows(rows, LimiterConfig(limit=2)))
    assert len(result) == 2


def test_apply_limit_convenience(rows: list[dict]) -> None:
    result = apply_limit(rows, limit=4, offset=1)
    assert len(result) == 4
    assert result[0]["id"] == 1


# ---------------------------------------------------------------------------
# limited_export
# ---------------------------------------------------------------------------


def test_generate_limited_rows_returns_list(simple_table: TableDefinition) -> None:
    cfg = LimiterConfig(limit=3)
    result = generate_limited_rows(simple_table, count=10, config=cfg)
    assert isinstance(result, list)
    assert len(result) == 3


def test_generate_limited_rows_negative_count_raises(simple_table: TableDefinition) -> None:
    with pytest.raises(ValueError, match="count"):
        generate_limited_rows(simple_table, count=-1, config=LimiterConfig())


def test_export_limited_returns_correct_count(simple_table: TableDefinition) -> None:
    result = export_limited(simple_table, count=8, limit=5)
    assert len(result) == 5


def test_export_limited_rows_have_expected_keys(simple_table: TableDefinition) -> None:
    result = export_limited(simple_table, count=5)
    for row in result:
        assert "id" in row
        assert "username" in row
