"""Export snapshots to JSON or CSV representations."""

from __future__ import annotations

import json
from typing import Any, Dict, List

from sqlseed.row_snapshot import Snapshot, diff_snapshots
from sqlseed.row_serializer import serialize_rows_csv, serialize_rows_json


def export_snapshot_json(snapshot: Snapshot, indent: int = 2) -> str:
    """Serialise a snapshot to a JSON string."""
    payload: Dict[str, Any] = {
        "name": snapshot.name,
        "table": snapshot.table,
        "row_count": len(snapshot),
        "rows": snapshot.rows,
    }
    return json.dumps(payload, indent=indent, default=str)


def export_snapshot_csv(snapshot: Snapshot) -> str:
    """Serialise a snapshot's rows to CSV."""
    if not snapshot.rows:
        return ""
    return serialize_rows_csv(snapshot.rows)


def export_diff_json(
    a: Snapshot, b: Snapshot, indent: int = 2
) -> str:
    """Return a JSON string describing the diff between two snapshots."""
    diff = diff_snapshots(a, b)
    return json.dumps(diff, indent=indent, default=str)


def export_snapshot(snapshot: Snapshot, fmt: str = "json") -> str:
    """Export a snapshot in the requested format ('json' or 'csv')."""
    fmt = fmt.lower()
    if fmt == "json":
        return export_snapshot_json(snapshot)
    if fmt == "csv":
        return export_snapshot_csv(snapshot)
    raise ValueError(f"Unsupported export format: {fmt!r}. Choose 'json' or 'csv'.")
