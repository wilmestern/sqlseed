"""Tests for sqlseed.batch_exporter."""

from __future__ import annotations

import pytest

from sqlseed.schema_parser import TableDefinition, ColumnDefinition
from sqlseed.batch_exporter import BatchExportConfig, export_tables, export_table_map


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def users_table() -> TableDefinition:
    return TableDefinition(
        name="users",
        columns=[
            ColumnDefinition(name="id", col_type="INTEGER", nullable=False, primary_key=True),
            ColumnDefinition(name="email", col_type="VARCHAR", nullable=False, max_length=255),
        ],
        foreign_keys=[],
    )


@pytest.fixture()
def posts_table() -> TableDefinition:
    return TableDefinition(
        name="posts",
        columns=[
            ColumnDefinition(name="id", col_type="INTEGER", nullable=False, primary_key=True),
            ColumnDefinition(name="user_id", col_type="INTEGER", nullable=False),
            ColumnDefinition(name="title", col_type="VARCHAR", nullable=False, max_length=200),
        ],
        foreign_keys=[],
    )


@pytest.fixture()
def config(users_table, posts_table) -> BatchExportConfig:
    return BatchExportConfig(
        tables=[users_table, posts_table],
        default_count=3,
        dialect="sqlite",
    )


# ---------------------------------------------------------------------------
# BatchExportConfig tests
# ---------------------------------------------------------------------------


def test_count_for_returns_default_when_not_set(config):
    assert config.count_for("users") == 3


def test_count_for_returns_override_when_set(users_table, posts_table):
    cfg = BatchExportConfig(
        tables=[users_table, posts_table],
        row_counts={"users": 7},
        default_count=2,
    )
    assert cfg.count_for("users") == 7
    assert cfg.count_for("posts") == 2


# ---------------------------------------------------------------------------
# export_tables tests
# ---------------------------------------------------------------------------


def test_export_tables_returns_string(config):
    result = export_tables(config)
    assert isinstance(result, str)


def test_export_tables_contains_insert_for_each_table(config):
    result = export_tables(config)
    assert "INSERT INTO" in result
    assert "users" in result
    assert "posts" in result


def test_export_tables_respects_row_count(users_table):
    cfg = BatchExportConfig(tables=[users_table], default_count=5, dialect="sqlite")
    result = export_tables(cfg)
    # Each row produces one INSERT; count occurrences of VALUES keyword
    assert result.count("VALUES") == 5


def test_export_tables_no_header(config):
    config.include_header = False
    result = export_tables(config)
    assert "sqlseed" not in result.lower() or result.startswith("INSERT")


def test_export_tables_accepts_pre_ordered_list(users_table, posts_table, config):
    """Passing an explicit order should not raise and should include both tables."""
    result = export_tables(config, ordered=[users_table, posts_table])
    assert "users" in result
    assert "posts" in result


# ---------------------------------------------------------------------------
# export_table_map tests
# ---------------------------------------------------------------------------


def test_export_table_map_returns_dict(config):
    result = export_table_map(config)
    assert isinstance(result, dict)


def test_export_table_map_has_entry_per_table(config):
    result = export_table_map(config)
    assert set(result.keys()) == {"users", "posts"}


def test_export_table_map_values_are_sql_strings(config):
    result = export_table_map(config)
    for sql in result.values():
        assert isinstance(sql, str)
        assert "INSERT INTO" in sql
