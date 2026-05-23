"""High-level helpers that combine row generation with limiting."""

from __future__ import annotations

from sqlseed.enriched_generator import generate_enriched_row
from sqlseed.row_limiter import LimiterConfig, limit_rows
from sqlseed.schema_parser import TableDefinition


def generate_limited_rows(
    table: TableDefinition,
    count: int,
    config: LimiterConfig,
) -> list[dict]:
    """Generate *count* rows for *table* then apply *config* limits.

    Parameters
    ----------
    table:
        The table whose schema drives value generation.
    count:
        Total rows to generate before limiting.
    config:
        :class:`~sqlseed.row_limiter.LimiterConfig` describing how to
        slice the generated rows.

    Returns
    -------
    list[dict]
        The rows that survive the limiting step.
    """
    if count < 0:
        raise ValueError("count must be a non-negative integer")

    rows = [generate_enriched_row(table) for _ in range(count)]
    return limit_rows(rows, config)


def export_limited(
    table: TableDefinition,
    count: int,
    *,
    limit: int | None = None,
    offset: int = 0,
) -> list[dict]:
    """Convenience function: generate and apply a simple offset + limit."""
    config = LimiterConfig(limit=limit, offset=offset)
    return generate_limited_rows(table, count, config)
