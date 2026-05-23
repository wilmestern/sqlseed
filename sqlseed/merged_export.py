"""High-level helpers that merge generated rows with existing baseline rows."""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence

from sqlseed.enriched_generator import generate_enriched_row
from sqlseed.row_merger import MergeConfig, Row, merge_rows, merge_summary
from sqlseed.schema_parser import TableDefinition


def generate_and_merge(
    table: TableDefinition,
    baseline: Sequence[Row],
    count: int,
    key_columns: List[str],
    prefer: str = "right",
) -> List[Row]:
    """Generate *count* new rows for *table* and merge them into *baseline*.

    Newly generated rows are treated as the *right* side of the merge so
    that, by default, they overwrite matching baseline values.
    """
    generated: List[Row] = [
        generate_enriched_row(table) for _ in range(count)
    ]
    config = MergeConfig(key_columns=key_columns, prefer=prefer)
    return merge_rows(list(baseline), generated, config)


def export_merged(
    table: TableDefinition,
    baseline: Sequence[Row],
    count: int,
    key_columns: List[str],
    prefer: str = "right",
) -> Dict[str, Any]:
    """Return merged rows together with a summary of changes.

    Returns a dict with keys ``table``, ``rows``, and ``summary``.
    """
    merged = generate_and_merge(
        table=table,
        baseline=baseline,
        count=count,
        key_columns=key_columns,
        prefer=prefer,
    )
    summary = merge_summary(before=baseline, after=merged)
    return {
        "table": table.name,
        "rows": merged,
        "summary": summary,
    }
