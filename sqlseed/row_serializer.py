"""Row serializer: converts generated row dicts into various output formats."""

from __future__ import annotations

import csv
import io
import json
from typing import Any, Dict, List, Literal, Sequence

from sqlseed.schema_parser import TableDefinition

SerializeFormat = Literal["json", "csv", "tsv"]


def _coerce(value: Any) -> Any:
    """Ensure value is JSON-serialisable."""
    if value is None:
        return None
    if isinstance(value, (int, float, bool, str)):
        return value
    return str(value)


def serialize_rows_json(
    rows: List[Dict[str, Any]],
    *,
    indent: int | None = 2,
) -> str:
    """Return *rows* serialised as a JSON array string."""
    coerced = [{k: _coerce(v) for k, v in row.items()} for row in rows]
    return json.dumps(coerced, indent=indent)


def serialize_rows_csv(
    rows: List[Dict[str, Any]],
    table: TableDefinition,
    *,
    delimiter: str = ",",
) -> str:
    """Return *rows* serialised as a CSV/TSV string with a header row."""
    if not rows:
        return ""
    columns: Sequence[str] = [col.name for col in table.columns]
    buf = io.StringIO()
    writer = csv.DictWriter(
        buf,
        fieldnames=columns,
        delimiter=delimiter,
        lineterminator="\n",
        extrasaction="ignore",
    )
    writer.writeheader()
    for row in rows:
        writer.writerow({k: ("" if v is None else str(v)) for k, v in row.items()})
    return buf.getvalue()


def serialize_rows(
    rows: List[Dict[str, Any]],
    table: TableDefinition,
    fmt: SerializeFormat = "json",
) -> str:
    """Dispatch serialisation to the appropriate format handler."""
    if fmt == "json":
        return serialize_rows_json(rows)
    if fmt == "csv":
        return serialize_rows_csv(rows, table, delimiter=",")
    if fmt == "tsv":
        return serialize_rows_csv(rows, table, delimiter="\t")
    raise ValueError(f"Unsupported serialization format: {fmt!r}")
