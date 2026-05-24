"""casted_export.py — Generate rows and apply type casting before export."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from sqlseed.schema_parser import TableDefinition
from sqlseed.enriched_generator import generate_enriched_row
from sqlseed.row_caster import CasterConfig, cast_rows


def generate_casted_rows(
    table: TableDefinition,
    count: int = 10,
    config: Optional[CasterConfig] = None,
) -> List[Dict[str, Any]]:
    """Generate *count* enriched rows and cast their values.

    Parameters
    ----------
    table:
        The table definition to generate rows for.
    count:
        Number of rows to produce.  Must be a positive integer.
    config:
        Optional :class:`CasterConfig` controlling cast behaviour.

    Returns
    -------
    list of dicts with values cast to their target Python types.

    Raises
    ------
    ValueError
        If *count* is less than 1.
    """
    if count < 1:
        raise ValueError(f"count must be a positive integer, got {count!r}")
    raw_rows = [generate_enriched_row(table) for _ in range(count)]
    return cast_rows(raw_rows, table, config)


def export_casted(
    table: TableDefinition,
    count: int = 10,
    config: Optional[CasterConfig] = None,
) -> Dict[str, Any]:
    """Return a summary dict containing table name and casted rows.

    Useful as a lightweight export payload before serialisation.

    Parameters
    ----------
    table:
        The table definition to generate rows for.
    count:
        Number of rows to produce.  Must be a positive integer.
    config:
        Optional :class:`CasterConfig` controlling cast behaviour.

    Returns
    -------
    dict with keys ``table``, ``count``, and ``rows``.
    """
    rows = generate_casted_rows(table, count=count, config=config)
    return {
        "table": table.name,
        "count": len(rows),
        "rows": rows,
    }
