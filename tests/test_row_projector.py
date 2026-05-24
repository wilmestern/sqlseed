"""Tests for sqlseed.row_projector and sqlseed.projected_export."""

from __future__ import annotations

import pytest

from sqlseed.row_projector import ProjectorConfig, ProjectorError, project_rows, project_columns
from sqlseed.projected_export import export_projected
from sqlseed.schema_parser import ColumnDefinition, TableDefinition


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def sample_rows():
    return [
        {"id": 1, "name": "Alice", "email": "alice@example.com", "age": 30},
        {"id": 2, "name": "Bob", "email": "bob@example.com", "age": 25},
    ]


@pytest.fixture()
def simple_table():
    return TableDefinition(
        name="users",
        columns=[
            ColumnDefinition("id", "INTEGER", nullable=False, primary_key=True),
            ColumnDefinition("name", "VARCHAR", nullable=False),
            ColumnDefinition("email", "VARCHAR", nullable=True),
        ],
    )


# ---------------------------------------------------------------------------
# ProjectorConfig
# ---------------------------------------------------------------------------

def test_projector_config_include_and_exclude_raises():
    with pytest.raises(ProjectorError):
        ProjectorConfig(include=["id"], exclude=["name"])


def test_projector_config_neither_is_valid():
    cfg = ProjectorConfig()
    assert cfg.include is None
    assert cfg.exclude is None


def test_projector_config_normalises_include_lowercase():
    cfg = ProjectorConfig(include=["ID", "Name"])
    assert cfg.include == ["id", "name"]


def test_projector_config_case_sensitive_preserves_case():
    cfg = ProjectorConfig(include=["ID", "Name"], case_sensitive=True)
    assert cfg.include == ["ID", "Name"]


# ---------------------------------------------------------------------------
# project (include)
# ---------------------------------------------------------------------------

def test_project_include_keeps_only_listed_columns(sample_rows):
    cfg = ProjectorConfig(include=["id", "name"])
    result = project_rows(sample_rows, cfg)
    assert all(set(r.keys()) == {"id", "name"} for r in result)


def test_project_include_case_insensitive(sample_rows):
    cfg = ProjectorConfig(include=["ID", "EMAIL"])
    result = project_rows(sample_rows, cfg)
    assert all("email" in r for r in result)
    assert all("name" not in r for r in result)


# ---------------------------------------------------------------------------
# project (exclude)
# ---------------------------------------------------------------------------

def test_project_exclude_drops_listed_columns(sample_rows):
    cfg = ProjectorConfig(exclude=["email", "age"])
    result = project_rows(sample_rows, cfg)
    assert all(set(r.keys()) == {"id", "name"} for r in result)


def test_project_exclude_case_insensitive(sample_rows):
    cfg = ProjectorConfig(exclude=["EMAIL"])
    result = project_rows(sample_rows, cfg)
    assert all("email" not in r for r in result)


# ---------------------------------------------------------------------------
# project (no config)
# ---------------------------------------------------------------------------

def test_project_no_config_returns_all_columns(sample_rows):
    cfg = ProjectorConfig()
    result = project_rows(sample_rows, cfg)
    assert result == sample_rows


# ---------------------------------------------------------------------------
# project_columns convenience wrapper
# ---------------------------------------------------------------------------

def test_project_columns_include(sample_rows):
    result = project_columns(sample_rows, include=["id"])
    assert all(list(r.keys()) == ["id"] for r in result)


def test_project_columns_exclude(sample_rows):
    result = project_columns(sample_rows, exclude=["age"])
    assert all("age" not in r for r in result)


# ---------------------------------------------------------------------------
# projected_export integration
# ---------------------------------------------------------------------------

def test_export_projected_returns_correct_count(simple_table):
    rows = export_projected(simple_table, 5, include=["id", "name"])
    assert len(rows) == 5


def test_export_projected_only_included_columns_present(simple_table):
    rows = export_projected(simple_table, 3, include=["name"])
    assert all(set(r.keys()) == {"name"} for r in rows)


def test_export_projected_excluded_column_absent(simple_table):
    rows = export_projected(simple_table, 3, exclude=["email"])
    assert all("email" not in r for r in rows)


def test_export_projected_zero_count_returns_empty(simple_table):
    rows = export_projected(simple_table, 0, include=["id"])
    assert rows == []


def test_export_projected_negative_count_raises(simple_table):
    with pytest.raises(ValueError):
        export_projected(simple_table, -1)
