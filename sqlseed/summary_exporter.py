"""Export RowSummary objects to JSON or plain-text reports."""

from __future__ import annotations

import json
from typing import Any, Dict, List, Sequence

from sqlseed.row_summarizer import RowSummary, summarize_rows
from sqlseed.schema_parser import TableDefinition
from sqlseed.enriched_generator import generate_enriched_row


def export_summary_json(summary: RowSummary, indent: int = 2) -> str:
    """Serialise a RowSummary to a JSON string."""
    return json.dumps(summary.as_dict(), indent=indent, default=str)


def export_summary_text(summary: RowSummary) -> str:
    """Render a RowSummary as a human-readable text report."""
    lines: List[str] = [
        f"Summary for table: {summary.table}",
        f"  Total rows : {summary.row_count}",
        f"  Columns    : {len(summary.column_summaries)}",
        "-" * 40,
    ]
    for col, cs in summary.column_summaries.items():
        lines.append(f"  {cs.column}")
        lines.append(f"    count        : {cs.count}")
        lines.append(f"    null_count   : {cs.null_count}")
        lines.append(f"    null_rate    : {cs.null_rate:.2%}")
        lines.append(f"    unique_count : {cs.unique_count}")
        lines.append(f"    samples      : {', '.join(cs.sample_values)}")
    return "\n".join(lines)


def summarize_table(
    table: TableDefinition,
    count: int = 10,
    overrides: Dict[str, Any] | None = None,
) -> RowSummary:
    """Generate *count* rows for *table* and return their summary."""
    overrides = overrides or {}
    rows = [generate_enriched_row(table, overrides) for _ in range(count)]
    return summarize_rows(table.name, rows)


def export_summary(
    summary: RowSummary,
    fmt: str = "json",
    indent: int = 2,
) -> str:
    """Dispatch to the appropriate exporter based on *fmt* ('json' or 'text')."""
    fmt = fmt.lower()
    if fmt == "json":
        return export_summary_json(summary, indent=indent)
    if fmt in ("text", "txt"):
        return export_summary_text(summary)
    raise ValueError(f"Unsupported summary format: {fmt!r}. Use 'json' or 'text'.")
