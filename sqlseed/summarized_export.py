"""Convenience helpers to generate rows and immediately summarize them."""

from __future__ import annotations

import json
from typing import Any, Dict, List, Sequence, Tuple

from sqlseed.schema_parser import TableDefinition
from sqlseed.enriched_generator import generate_enriched_row
from sqlseed.row_summarizer import RowSummary, summarize_rows
from sqlseed.summary_exporter import export_summary_json, export_summary_text


def generate_and_summarize(
    table: TableDefinition,
    count: int = 10,
    overrides: Dict[str, Any] | None = None,
) -> Tuple[List[Dict[str, Any]], RowSummary]:
    """Return (rows, summary) for *count* generated rows."""
    overrides = overrides or {}
    rows = [generate_enriched_row(table, overrides) for _ in range(count)]
    summary = summarize_rows(table.name, rows)
    return rows, summary


def export_with_summary(
    table: TableDefinition,
    count: int = 10,
    summary_fmt: str = "json",
    overrides: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """Generate rows and return a dict with 'rows' and 'summary' keys."""
    rows, summary = generate_and_summarize(table, count=count, overrides=overrides)
    if summary_fmt.lower() == "text":
        rendered = export_summary_text(summary)
    else:
        rendered = json.loads(export_summary_json(summary))
    return {"rows": rows, "summary": rendered}


def multi_table_summary(
    tables: Sequence[TableDefinition],
    count: int = 10,
    overrides: Dict[str, Any] | None = None,
) -> Dict[str, RowSummary]:
    """Generate rows for multiple tables and return a mapping of table name -> RowSummary."""
    result: Dict[str, RowSummary] = {}
    for table in tables:
        _, summary = generate_and_summarize(table, count=count, overrides=overrides)
        result[table.name] = summary
    return result
