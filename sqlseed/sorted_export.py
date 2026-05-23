"""Sorted export: generate rows and apply ordering before serialisation."""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional

from sqlseed.enriched_generator import generate_enriched_row
from sqlseed.row_sorter import RowSorter
from sqlseed.schema_parser import TableDefinition


def generate_sorted_rows(
    table: TableDefinition,
    count: int,
    sorter: RowSorter,
    overrides: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """Generate *count* rows for *table*, then return them sorted via *sorter*.

    Parameters
    ----------
    table:
        The table definition used to generate values.
    count:
        Number of rows to generate before sorting.
    sorter:
        A configured :class:`~sqlseed.row_sorter.RowSorter` instance.
    overrides:
        Optional column-level value overrides forwarded to the generator.

    Returns
    -------
    list[dict]
        Sorted list of row dictionaries.
    """
    if count < 0:
        raise ValueError(f"count must be non-negative, got {count}.")

    rows: List[Dict[str, Any]] = [
        generate_enriched_row(table, overrides=overrides or {})
        for _ in range(count)
    ]
    return sorter.sort(rows)


def generate_sorted_rows_by(
    table: TableDefinition,
    count: int,
    column: str,
    ascending: bool = True,
    key_fn: Optional[Callable[[Any], Any]] = None,
    overrides: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """Convenience wrapper: generate rows sorted by a single *column*.

    Parameters
    ----------
    table:
        The table definition used to generate values.
    count:
        Number of rows to generate.
    column:
        Column name to sort by.
    ascending:
        Sort direction (default: ``True``).
    key_fn:
        Optional custom sort key function applied to each cell value.
    overrides:
        Optional column-level value overrides.

    Returns
    -------
    list[dict]
        Sorted list of row dictionaries.
    """
    sorter = RowSorter()
    sorter.add(column, ascending=ascending, key_fn=key_fn)
    return generate_sorted_rows(table, count, sorter, overrides=overrides)
