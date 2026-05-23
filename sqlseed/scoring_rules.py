"""Built-in scoring rules for RowScorer."""

from __future__ import annotations

from typing import Any, Dict

from sqlseed.schema_parser import TableDefinition


def completeness_rule(row: Dict[str, Any], table: TableDefinition) -> float:
    """Fraction of non-null values in the row."""
    if not table.columns:
        return 1.0
    non_null = sum(1 for col in table.columns if row.get(col.name) is not None)
    return non_null / len(table.columns)


def string_length_rule(row: Dict[str, Any], table: TableDefinition) -> float:
    """Penalises string columns that are empty or exceed max_length."""
    string_cols = [
        col for col in table.columns
        if col.data_type.upper() in ("VARCHAR", "TEXT", "CHAR")
    ]
    if not string_cols:
        return 1.0

    passed = 0
    for col in string_cols:
        val = row.get(col.name)
        if val is None:
            passed += 1
            continue
        s = str(val)
        if len(s) == 0:
            continue
        if col.max_length is not None and len(s) > col.max_length:
            continue
        passed += 1

    return passed / len(string_cols)


def no_placeholder_rule(row: Dict[str, Any], table: TableDefinition) -> float:
    """Penalises rows containing obvious placeholder values like 'N/A' or 'TBD'."""
    placeholders = {"n/a", "tbd", "todo", "fixme", "placeholder", "test", "example"}
    total = len(row)
    if total == 0:
        return 1.0
    clean = sum(
        1 for v in row.values()
        if not (isinstance(v, str) and v.strip().lower() in placeholders)
    )
    return clean / total


def numeric_range_rule(row: Dict[str, Any], table: TableDefinition) -> float:
    """Checks that numeric columns contain finite, reasonable values."""
    import math
    numeric_types = ("INT", "INTEGER", "BIGINT", "SMALLINT", "FLOAT", "DOUBLE", "DECIMAL", "NUMERIC", "REAL")
    numeric_cols = [
        col for col in table.columns
        if any(col.data_type.upper().startswith(t) for t in numeric_types)
    ]
    if not numeric_cols:
        return 1.0

    passed = 0
    for col in numeric_cols:
        val = row.get(col.name)
        if val is None:
            passed += 1
            continue
        try:
            f = float(val)
            if math.isfinite(f):
                passed += 1
        except (TypeError, ValueError):
            pass

    return passed / len(numeric_cols)
