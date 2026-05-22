"""Export formatter: wraps row_serializer to produce labelled, multi-table exports."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

from sqlseed.row_serializer import SerializeFormat, serialize_rows
from sqlseed.schema_parser import TableDefinition


@dataclass
class TableExport:
    table: TableDefinition
    rows: List[Dict[str, Any]]


@dataclass
class ExportBundle:
    """Holds multiple table exports and renders them as a single string."""

    exports: List[TableExport] = field(default_factory=list)
    fmt: SerializeFormat = "json"

    def add(self, table: TableDefinition, rows: List[Dict[str, Any]]) -> None:
        """Append a table's rows to this bundle."""
        self.exports.append(TableExport(table=table, rows=rows))

    def render(self) -> str:
        """Render all table exports separated by a labelled header."""
        parts: List[str] = []
        for export in self.exports:
            header = f"-- Table: {export.table.name}"
            body = serialize_rows(export.rows, export.table, fmt=self.fmt)
            parts.append(f"{header}\n{body}")
        return "\n\n".join(parts)


def format_export(
    tables: List[TableDefinition],
    rows_map: Dict[str, List[Dict[str, Any]]],
    fmt: SerializeFormat = "json",
) -> str:
    """Convenience function: build and render an ExportBundle from a map of rows."""
    bundle = ExportBundle(fmt=fmt)
    for table in tables:
        rows = rows_map.get(table.name, [])
        bundle.add(table, rows)
    return bundle.render()
