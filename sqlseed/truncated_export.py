"""Convenience helpers that generate rows and apply truncation in one step."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from sqlseed.enriched_generator import generate_enriched_row
from sqlseed.row_truncator import TruncatorConfig, truncate_rows
from sqlseed.schema_parser import TableDefinition


def generate_truncated_rows(
    table: TableDefinition,
    count: int,
    config: TruncatorConfig,
) -> List[Dict[str, Any]]:
    """Generate *count* rows for *table* and truncate string values.

    Parameters
    ----------
    table:
        Parsed table definition used for row generation.
    count:
        Number of rows to produce.
    config:
        Truncation settings applied after generation.

    Returns
    -------
    list[dict]
        Truncated rows ready for export.
    """
    if count < 0:
        raise ValueError("count must be a non-negative integer.")
    rows = [generate_enriched_row(table) for _ in range(count)]
    return truncate_rows(rows, config)


def export_truncated(
    table: TableDefinition,
    count: int,
    global_max_length: Optional[int] = None,
    column_limits: Optional[Dict[str, int]] = None,
    ellipsis: str = "",
) -> List[Dict[str, Any]]:
    """High-level helper: build a :class:`TruncatorConfig` inline and export.

    Parameters
    ----------
    table:
        Table definition to generate data for.
    count:
        Number of rows to generate.
    global_max_length:
        Optional cap applied to every string column.
    column_limits:
        Optional per-column overrides (column name → max length).
    ellipsis:
        String appended to truncated values (e.g. ``"…"``).  Counts towards
        the length budget.

    Returns
    -------
    list[dict]
        Generated and truncated rows.
    """
    config = TruncatorConfig(
        global_max_length=global_max_length,
        column_limits=column_limits or {},
        ellipsis=ellipsis,
    )
    return generate_truncated_rows(table, count, config)
