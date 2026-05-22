"""Tests for sqlseed.row_sampler."""

from __future__ import annotations

import pytest

from sqlseed.row_sampler import (
    SamplerConfig,
    SamplingError,
    sample_rows,
    sample_table,
)
from sqlseed.schema_parser import ColumnDefinition, TableDefinition


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def rows() -> list[dict]:
    return [{"id": i, "name": f"user_{i}", "active": i % 2 == 0} for i in range(20)]


@pytest.fixture()
def simple_table() -> TableDefinition:
    col = ColumnDefinition(name="id", col_type="INTEGER", nullable=False, primary_key=True)
    return TableDefinition(name="items", columns=[col])


# ---------------------------------------------------------------------------
# SamplerConfig validation
# ---------------------------------------------------------------------------


def test_sampler_config_default_strategy():
    cfg = SamplerConfig()
    assert cfg.strategy == "random"


def test_sampler_config_invalid_strategy_raises():
    with pytest.raises(ValueError, match="Invalid sampling strategy"):
        SamplerConfig(strategy="middle")


def test_sampler_config_valid_strategies():
    for s in ("random", "first", "last"):
        cfg = SamplerConfig(strategy=s)
        assert cfg.strategy == s


# ---------------------------------------------------------------------------
# sample_rows — basic behaviour
# ---------------------------------------------------------------------------


def test_sample_rows_negative_n_raises(rows):
    with pytest.raises(SamplingError):
        sample_rows(rows, -1)


def test_sample_rows_zero_returns_empty(rows):
    assert sample_rows(rows, 0) == []


def test_sample_rows_returns_correct_count(rows):
    result = sample_rows(rows, 5, SamplerConfig(strategy="first"))
    assert len(result) == 5


def test_sample_rows_first_strategy_preserves_order(rows):
    result = sample_rows(rows, 3, SamplerConfig(strategy="first"))
    assert result == rows[:3]


def test_sample_rows_last_strategy_preserves_order(rows):
    result = sample_rows(rows, 3, SamplerConfig(strategy="last"))
    assert result == rows[-3:]


def test_sample_rows_random_is_deterministic_with_seed(rows):
    cfg = SamplerConfig(strategy="random", seed=42)
    r1 = sample_rows(rows, 5, cfg)
    r2 = sample_rows(rows, 5, cfg)
    assert r1 == r2


def test_sample_rows_random_different_seeds_differ(rows):
    r1 = sample_rows(rows, 10, SamplerConfig(strategy="random", seed=1))
    r2 = sample_rows(rows, 10, SamplerConfig(strategy="random", seed=99))
    assert r1 != r2


def test_sample_rows_n_larger_than_pool_returns_all(rows):
    result = sample_rows(rows, 1000, SamplerConfig(strategy="first"))
    assert len(result) == len(rows)


# ---------------------------------------------------------------------------
# sample_rows — predicate filtering
# ---------------------------------------------------------------------------


def test_sample_rows_predicate_filters_candidates(rows):
    cfg = SamplerConfig(strategy="first", predicate=lambda r: r["active"])
    result = sample_rows(rows, 100, cfg)
    assert all(r["active"] for r in result)


def test_sample_rows_predicate_none_match_returns_empty(rows):
    cfg = SamplerConfig(strategy="first", predicate=lambda r: r["id"] > 1000)
    result = sample_rows(rows, 5, cfg)
    assert result == []


# ---------------------------------------------------------------------------
# sample_table
# ---------------------------------------------------------------------------


def test_sample_table_empty_rows_returns_empty(simple_table):
    assert sample_table(simple_table, [], 10) == []


def test_sample_table_returns_correct_count(simple_table, rows):
    result = sample_table(simple_table, rows, 4, SamplerConfig(strategy="first"))
    assert len(result) == 4
