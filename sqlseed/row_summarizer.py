"""Row summarizer: produce statistical summaries of generated row sets."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence


@dataclass
class ColumnSummary:
    column: str
    count: int
    null_count: int
    unique_count: int
    sample_values: List[Any] = field(default_factory=list)

    @property
    def null_rate(self) -> float:
        if self.count == 0:
            return 0.0
        return self.null_count / self.count

    def __str__(self) -> str:
        return (
            f"ColumnSummary({self.column!r}: count={self.count}, "
            f"nulls={self.null_count}, unique={self.unique_count})"
        )


@dataclass
class RowSummary:
    table: str
    row_count: int
    column_summaries: Dict[str, ColumnSummary] = field(default_factory=dict)

    def get(self, column: str) -> Optional[ColumnSummary]:
        return self.column_summaries.get(column.lower())

    def as_dict(self) -> Dict[str, Any]:
        return {
            "table": self.table,
            "row_count": self.row_count,
            "columns": {
                col: {
                    "count": cs.count,
                    "null_count": cs.null_count,
                    "null_rate": round(cs.null_rate, 4),
                    "unique_count": cs.unique_count,
                    "sample_values": cs.sample_values,
                }
                for col, cs in self.column_summaries.items()
            },
        }

    def __str__(self) -> str:
        return f"RowSummary(table={self.table!r}, rows={self.row_count}, columns={len(self.column_summaries)})"


_SAMPLE_LIMIT = 3


def summarize_rows(table_name: str, rows: Sequence[Dict[str, Any]]) -> RowSummary:
    """Compute a RowSummary for a list of row dicts."""
    if not rows:
        return RowSummary(table=table_name, row_count=0)

    columns = list(rows[0].keys())
    summaries: Dict[str, ColumnSummary] = {}

    for col in columns:
        values = [row.get(col) for row in rows]
        null_count = sum(1 for v in values if v is None)
        non_null = [v for v in values if v is not None]
        unique_count = len(set(str(v) for v in non_null))
        sample = list(dict.fromkeys(str(v) for v in non_null))[:_SAMPLE_LIMIT]
        summaries[col.lower()] = ColumnSummary(
            column=col,
            count=len(values),
            null_count=null_count,
            unique_count=unique_count,
            sample_values=sample,
        )

    return RowSummary(table=table_name, row_count=len(rows), column_summaries=summaries)
