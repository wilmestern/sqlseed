"""Filtered seed generation for sqlseed.

Combines validated row generation with RowFilter to produce rows that
satisfy both schema constraints and caller-supplied predicates.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from sqlseed.schema_parser import TableDefinition
from sqlseed.validated_seed import generate_valid_row, RowGenerationError
from sqlseed.row_filter import RowFilter

Row = Dict[str, Any]


class FilteredGenerationError(Exception):
    """Raised when a valid, filter-passing row cannot be produced."""


def generate_filtered_row(
    table: TableDefinition,
    row_filter: Optional[RowFilter] = None,
    max_attempts: int = 100,
) -> Row:
    """Generate a single row that passes schema validation and *row_filter*.

    Parameters
    ----------
    table:
        Table definition used for generation and validation.
    row_filter:
        Optional :class:`RowFilter` instance.  If *None*, no extra filtering
        is applied beyond schema constraints.
    max_attempts:
        Maximum number of generation attempts before raising
        :class:`FilteredGenerationError`.

    Raises
    ------
    FilteredGenerationError
        If no valid, filter-passing row is produced within *max_attempts*.
    """
    for attempt in range(max_attempts):
        try:
            row = generate_valid_row(table)
        except RowGenerationError:
            continue
        if row_filter is None or row_filter.passes(row):
            return row
    raise FilteredGenerationError(
        f"Could not generate a row for table '{table.name}' that satisfies "
        f"all filters within {max_attempts} attempts."
    )


def generate_filtered_rows(
    table: TableDefinition,
    count: int,
    row_filter: Optional[RowFilter] = None,
    max_attempts: int = 100,
) -> List[Row]:
    """Generate *count* rows, each passing schema validation and *row_filter*.

    Parameters
    ----------
    table:
        Table definition used for generation.
    count:
        Number of rows to produce.
    row_filter:
        Optional :class:`RowFilter` instance applied to every row.
    max_attempts:
        Per-row attempt budget passed to :func:`generate_filtered_row`.
    """
    return [
        generate_filtered_row(table, row_filter=row_filter, max_attempts=max_attempts)
        for _ in range(count)
    ]
