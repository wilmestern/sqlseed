"""Human-readable and machine-readable reporting for DiffReport objects."""

from __future__ import annotations

import json
from typing import Any, Dict, List

from sqlseed.row_diff import DiffReport, RowDiff


def _row_diff_to_dict(rd: RowDiff) -> Dict[str, Any]:
    return {
        "index": rd.index,
        "changes": [
            {"column": d.column, "left": d.left, "right": d.right}
            for d in rd.diffs
        ],
    }


def report_to_dict(report: DiffReport) -> Dict[str, Any]:
    """Serialise a DiffReport to a plain dictionary."""
    return {
        "table": report.table_name,
        "has_differences": report.has_differences,
        "changed_rows": [
            _row_diff_to_dict(r) for r in report.row_diffs if r.has_changes
        ],
        "only_in_left": report.only_in_left,
        "only_in_right": report.only_in_right,
    }


def report_to_json(report: DiffReport, indent: int = 2) -> str:
    """Serialise a DiffReport to a JSON string."""
    return json.dumps(report_to_dict(report), indent=indent, default=str)


def report_to_text(report: DiffReport) -> str:
    """Render a DiffReport as a human-readable text block."""
    lines: List[str] = [report.summary()]

    changed = [r for r in report.row_diffs if r.has_changes]
    if changed:
        lines.append("Changed rows:")
        for rd in changed:
            lines.append(f"  {rd}")

    if report.only_in_left:
        indices = ", ".join(str(i) for i in report.only_in_left)
        lines.append(f"Only in left  (indices): {indices}")

    if report.only_in_right:
        indices = ", ".join(str(i) for i in report.only_in_right)
        lines.append(f"Only in right (indices): {indices}")

    if not report.has_differences:
        lines.append("No differences found.")

    return "\n".join(lines)


def format_diff_report(report: DiffReport, fmt: str = "text") -> str:
    """Dispatch to the appropriate renderer based on *fmt*.

    Supported formats: ``"text"``, ``"json"``.
    """
    fmt = fmt.lower()
    if fmt == "json":
        return report_to_json(report)
    if fmt == "text":
        return report_to_text(report)
    raise ValueError(f"Unsupported diff report format: {fmt!r}. Choose 'text' or 'json'.")
