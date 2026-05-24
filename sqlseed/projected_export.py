"""Projected export: generate rows and project their columns in one step."""

from __future__ import annotations

from typing import Dict, List, Optional

from sqlseed.enriched_generator import generate_enriched_row
from sqlseed.row_projector import ProjectorConfig, project_rows
from sqlseed.schema_parser import TableDefinition


def generate_projected_rows(
    table: TableDefinition,
    count: int,
    config: ProjectorConfig,
) -> List[Dict]:
    """Generate *count* rows for *table* and apply column projection."""
    if count < 0:
        raise ValueError("count must be >= 0")
    raw = [generate_enriched_row(table) for _ in range(count)]
    return project_rows(raw, config)


def export_projected(
    table: TableDefinition,
    count: int,
    include: Optional[List[str]] = None,
    exclude: Optional[List[str]] = None,
    case_sensitive: bool = False,
) -> List[Dict]:
    """Generate and project rows using include/exclude column lists.

    Parameters
    ----------
    table:
        The table definition to generate data for.
    count:
        Number of rows to generate.
    include:
        Whitelist of column names to keep.  Mutually exclusive with *exclude*.
    exclude:
        Blacklist of column names to drop.  Mutually exclusive with *include*.
    case_sensitive:
        Whether column name matching is case-sensitive (default: False).
    """
    cfg = ProjectorConfig(
        include=include,
        exclude=exclude,
        case_sensitive=case_sensitive,
    )
    return generate_projected_rows(table, count, cfg)
