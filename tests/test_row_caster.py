"""Tests for sqlseed.row_caster and sqlseed.casted_export."""

from __future__ import annotations

import pytest

from sqlseed.schema_parser import TableDefinition, ColumnDefinition
from sqlseed.row_caster import CasterConfig, CastError, cast_row, cast_rows
from sqlseed.casted_export import generate_casted_rows, export_casted


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def simple_table() -> TableDefinition:
    return TableDefinition(
        name="products",
        columns=[
            ColumnDefinition(name="id", col_type="INTEGER", nullable=False, primary_key=True),
            ColumnDefinition(name="name", col_type="VARCHAR(100)", nullable=False),
            ColumnDefinition(name="price", col_type="REAL", nullable=True),
            ColumnDefinition(name="in_stock", col_type="BOOLEAN", nullable=True),
        ],
    )


# ---------------------------------------------------------------------------
# CasterConfig
# ---------------------------------------------------------------------------

def test_caster_config_defaults():
    cfg = CasterConfig()
    assert cfg.strict is False
    assert cfg.custom == {}


def test_caster_config_normalises_custom_keys_lowercase():
    cfg = CasterConfig(custom={"Price": float, "NAME": str})
    assert "price" in cfg.custom
    assert "name" in cfg.custom


# ---------------------------------------------------------------------------
# cast_row
# ---------------------------------------------------------------------------

def test_cast_row_returns_dict(simple_table):
    row = {"id": "1", "name": "Widget", "price": "9.99", "in_stock": "True"}
    result = cast_row(row, simple_table)
    assert isinstance(result, dict)


def test_cast_row_integer_column_cast(simple_table):
    row = {"id": "42", "name": "Widget", "price": None, "in_stock": None}
    result = cast_row(row, simple_table)
    assert result["id"] == 42
    assert isinstance(result["id"], int)


def test_cast_row_real_column_cast(simple_table):
    row = {"id": 1, "name": "Widget", "price": "3.14", "in_stock": None}
    result = cast_row(row, simple_table)
    assert isinstance(result["price"], float)
    assert abs(result["price"] - 3.14) < 1e-9


def test_cast_row_none_preserved(simple_table):
    row = {"id": 1, "name": "Widget", "price": None, "in_stock": None}
    result = cast_row(row, simple_table)
    assert result["price"] is None
    assert result["in_stock"] is None


def test_cast_row_preserves_all_columns(simple_table):
    row = {"id": 1, "name": "Widget", "price": 1.0, "in_stock": True}
    result = cast_row(row, simple_table)
    assert set(result.keys()) == {"id", "name", "price", "in_stock"}


def test_cast_row_strict_raises_on_bad_value(simple_table):
    row = {"id": "not-an-int", "name": "Widget", "price": None, "in_stock": None}
    cfg = CasterConfig(strict=True)
    with pytest.raises(CastError):
        cast_row(row, simple_table, cfg)


def test_cast_row_non_strict_leaves_bad_value_unchanged(simple_table):
    row = {"id": "not-an-int", "name": "Widget", "price": None, "in_stock": None}
    cfg = CasterConfig(strict=False)
    result = cast_row(row, simple_table, cfg)
    assert result["id"] == "not-an-int"


def test_cast_row_custom_override_applied(simple_table):
    cfg = CasterConfig(custom={"price": lambda v: round(float(v), 2)})
    row = {"id": 1, "name": "Widget", "price": "9.999", "in_stock": None}
    result = cast_row(row, simple_table, cfg)
    assert result["price"] == 10.0


# ---------------------------------------------------------------------------
# cast_rows
# ---------------------------------------------------------------------------

def test_cast_rows_returns_list(simple_table):
    rows = [
        {"id": "1", "name": "A", "price": "1.0", "in_stock": True},
        {"id": "2", "name": "B", "price": "2.0", "in_stock": False},
    ]
    result = cast_rows(rows, simple_table)
    assert isinstance(result, list)
    assert len(result) == 2


def test_cast_rows_does_not_mutate_input(simple_table):
    rows = [{"id": "1", "name": "A", "price": "1.0", "in_stock": True}]
    cast_rows(rows, simple_table)
    assert rows[0]["id"] == "1"  # original unchanged


# ---------------------------------------------------------------------------
# casted_export
# ---------------------------------------------------------------------------

def test_generate_casted_rows_count(simple_table):
    rows = generate_casted_rows(simple_table, count=5)
    assert len(rows) == 5


def test_generate_casted_rows_are_dicts(simple_table):
    rows = generate_casted_rows(simple_table, count=3)
    for row in rows:
        assert isinstance(row, dict)


def test_export_casted_structure(simple_table):
    result = export_casted(simple_table, count=4)
    assert result["table"] == "products"
    assert result["count"] == 4
    assert len(result["rows"]) == 4
