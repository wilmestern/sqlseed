"""Tests for sqlseed.row_renamer and sqlseed.renamed_export."""
from __future__ import annotations

import pytest

from sqlseed.row_renamer import (
    RenameConfig,
    RenamerError,
    rename_row,
    rename_rows,
)
from sqlseed.renamed_export import export_renamed, generate_renamed_rows
from sqlseed.schema_parser import ColumnDefinition, TableDefinition


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _simple_table() -> TableDefinition:
    return TableDefinition(
        name="users",
        columns=[
            ColumnDefinition(name="id", col_type="INTEGER", nullable=False, primary_key=True),
            ColumnDefinition(name="email", col_type="VARCHAR", nullable=False, primary_key=False),
            ColumnDefinition(name="created_at", col_type="DATETIME", nullable=True, primary_key=False),
        ],
    )


# ---------------------------------------------------------------------------
# RenameConfig
# ---------------------------------------------------------------------------

def test_rename_config_add_registers_mapping():
    cfg = RenameConfig()
    cfg.add("email", "email_address")
    assert "email" in cfg.sources()


def test_rename_config_add_empty_source_raises():
    cfg = RenameConfig()
    with pytest.raises(RenamerError):
        cfg.add("", "target")


def test_rename_config_add_empty_target_raises():
    cfg = RenameConfig()
    with pytest.raises(RenamerError):
        cfg.add("source", "")


def test_rename_config_remove_existing():
    cfg = RenameConfig()
    cfg.add("email", "email_address")
    cfg.remove("email")
    assert "email" not in cfg.sources()


def test_rename_config_remove_unknown_does_not_raise():
    cfg = RenameConfig()
    cfg.remove("nonexistent")  # should not raise


def test_rename_config_clear_removes_all():
    cfg = RenameConfig()
    cfg.add("email", "email_address")
    cfg.add("id", "user_id")
    cfg.clear()
    assert cfg.sources() == []


def test_rename_config_case_insensitive_normalises_key():
    cfg = RenameConfig(case_sensitive=False)
    cfg.add("Email", "email_address")
    assert "email" in cfg.sources()


def test_rename_config_case_sensitive_preserves_key():
    cfg = RenameConfig(case_sensitive=True)
    cfg.add("Email", "email_address")
    assert "Email" in cfg.sources()
    assert "email" not in cfg.sources()


# ---------------------------------------------------------------------------
# rename_row
# ---------------------------------------------------------------------------

def test_rename_row_applies_mapping():
    cfg = RenameConfig(mapping={"email": "email_address"})
    row = {"id": 1, "email": "a@b.com"}
    result = rename_row(row, cfg)
    assert "email_address" in result
    assert "email" not in result


def test_rename_row_preserves_unmapped_columns():
    cfg = RenameConfig(mapping={"email": "email_address"})
    row = {"id": 1, "email": "a@b.com"}
    result = rename_row(row, cfg)
    assert "id" in result


def test_rename_row_collision_raises():
    cfg = RenameConfig(mapping={"email": "id"}, case_sensitive=True)
    row = {"id": 1, "email": "a@b.com"}
    with pytest.raises(RenamerError):
        rename_row(row, cfg)


def test_rename_rows_applies_to_all():
    cfg = RenameConfig(mapping={"email": "email_address"})
    rows = [{"id": i, "email": f"u{i}@x.com"} for i in range(3)]
    result = rename_rows(rows, cfg)
    assert all("email_address" in r for r in result)
    assert all("email" not in r for r in result)


# ---------------------------------------------------------------------------
# renamed_export
# ---------------------------------------------------------------------------

def test_generate_renamed_rows_count():
    table = _simple_table()
    cfg = RenameConfig(mapping={"email": "email_address"})
    rows = generate_renamed_rows(table, 5, cfg)
    assert len(rows) == 5


def test_generate_renamed_rows_negative_count_raises():
    table = _simple_table()
    cfg = RenameConfig()
    with pytest.raises(ValueError):
        generate_renamed_rows(table, -1, cfg)


def test_export_renamed_applies_mapping():
    table = _simple_table()
    rows = export_renamed(table, 3, {"email": "email_address"})
    assert all("email_address" in r for r in rows)


def test_export_renamed_zero_count_returns_empty():
    table = _simple_table()
    rows = export_renamed(table, 0, {})
    assert rows == []
