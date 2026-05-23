"""Generate rows and immediately group them by key columns."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from sqlseed.enriched_generator import generate_enriched_row
from sqlseed.row_grouper import GrouperConfig, group_rows
from sqlseed.schema_parser import TableDefinition


class GroupedGenerationError(Exception):
    """Raised when grouped row generation fails."""


def generate_grouped_rows(
    table: TableDefinition,
    count: int,
    config: GrouperConfig,
    *,
    max_attempts: int = 10,
) -> Dict[Tuple[Any, ...], List[Dict[str, Any]]]:
    """Generate *count* rows for *table* and return them partitioned by *config*.

    Parameters
    ----------
    table:
        The table definition used to generate rows.
    count:
        Total number of rows to generate before grouping.
    config:
        Grouping configuration (key columns, case sensitivity).
    max_attempts:
        Maximum generation attempts per row before raising.
    """
    if count < 0:
        raise GroupedGenerationError("count must be a non-negative integer")

    rows: List[Dict[str, Any]] = []
    for _ in range(count):
        attempts = 0
        while attempts < max_attempts:
            try:
                row = generate_enriched_row(table)
                rows.append(row)
                break
            except Exception as exc:  # noqa: BLE001
                attempts += 1
                if attempts >= max_attempts:
                    raise GroupedGenerationError(
                        f"Failed to generate a valid row after {max_attempts} attempts"
                    ) from exc

    return group_rows(rows, config)


def generate_grouped_rows_flat(
    table: TableDefinition,
    count: int,
    config: GrouperConfig,
) -> List[Dict[str, Any]]:
    """Generate *count* rows and return them sorted by their group key.

    Rows within the same group are kept together; the overall order follows
    the natural iteration order of the groups dict (insertion order).
    """
    groups = generate_grouped_rows(table, count, config)
    flat: List[Dict[str, Any]] = []
    for rows in groups.values():
        flat.extend(rows)
    return flat
