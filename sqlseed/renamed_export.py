"""Renamed export — generate rows and apply column renaming in one step."""
from __future__ import annotations

from typing import Dict, List, Optional

from sqlseed.enriched_generator import generate_enriched_row
from sqlseed.row_renamer import RenameConfig, rename_rows
from sqlseed.schema_parser import TableDefinition


def generate_renamed_rows(
    table: TableDefinition,
    count: int,
    config: RenameConfig,
    seed: Optional[int] = None,
) -> List[Dict[str, object]]:
    """Generate *count* rows for *table* and rename columns per *config*.

    Args:
        table:  The table definition to generate data for.
        count:  Number of rows to produce.
        config: Rename configuration mapping old column names to new ones.
        seed:   Optional random seed for reproducibility (currently unused
                but reserved for future deterministic generation support).

    Returns:
        A list of dicts with renamed column keys.
    """
    if count < 0:
        raise ValueError("count must be a non-negative integer.")

    raw_rows: List[Dict[str, object]] = [
        generate_enriched_row(table) for _ in range(count)
    ]
    return rename_rows(raw_rows, config)


def export_renamed(
    table: TableDefinition,
    count: int,
    mapping: Dict[str, str],
    case_sensitive: bool = False,
) -> List[Dict[str, object]]:
    """Convenience wrapper: build a :class:`RenameConfig` and generate rows.

    Args:
        table:          Table definition.
        count:          Number of rows.
        mapping:        Dict of ``{original_column: new_column}`` renames.
        case_sensitive: Whether column matching is case-sensitive.

    Returns:
        Renamed rows as a list of dicts.
    """
    config = RenameConfig(mapping=mapping, case_sensitive=case_sensitive)
    return generate_renamed_rows(table, count, config)
