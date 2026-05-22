"""Row diff utility: compare two sets of generated rows and report field-level differences."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class FieldDiff:
    column: str
    left: Any
    right: Any

    def __str__(self) -> str:
        return f"{self.column}: {self.left!r} -> {self.right!r}"


@dataclass
class RowDiff:
    index: int
    diffs: List[FieldDiff] = field(default_factory=list)

    @property
    def has_changes(self) -> bool:
        return len(self.diffs) > 0

    def __str__(self) -> str:
        changes = ", ".join(str(d) for d in self.diffs)
        return f"Row {self.index}: [{changes}]"


@dataclass
class DiffReport:
    table_name: str
    row_diffs: List[RowDiff] = field(default_factory=list)
    only_in_left: List[int] = field(default_factory=list)
    only_in_right: List[int] = field(default_factory=list)

    @property
    def has_differences(self) -> bool:
        return (
            any(r.has_changes for r in self.row_diffs)
            or bool(self.only_in_left)
            or bool(self.only_in_right)
        )

    def summary(self) -> str:
        changed = sum(1 for r in self.row_diffs if r.has_changes)
        return (
            f"Table '{self.table_name}': {changed} changed row(s), "
            f"{len(self.only_in_left)} only-left, {len(self.only_in_right)} only-right."
        )


def diff_row(
    index: int,
    left: Dict[str, Any],
    right: Dict[str, Any],
    columns: Optional[List[str]] = None,
) -> RowDiff:
    """Compare two row dicts and return a RowDiff describing field-level changes."""
    cols = columns if columns is not None else sorted(set(left) | set(right))
    diffs = [
        FieldDiff(col, left.get(col), right.get(col))
        for col in cols
        if left.get(col) != right.get(col)
    ]
    return RowDiff(index=index, diffs=diffs)


def diff_rows(
    table_name: str,
    left: List[Dict[str, Any]],
    right: List[Dict[str, Any]],
    columns: Optional[List[str]] = None,
) -> DiffReport:
    """Compare two lists of rows for the same table and return a DiffReport."""
    report = DiffReport(table_name=table_name)
    min_len = min(len(left), len(right))

    for i in range(min_len):
        row_diff = diff_row(i, left[i], right[i], columns)
        report.row_diffs.append(row_diff)

    report.only_in_left = list(range(min_len, len(left)))
    report.only_in_right = list(range(min_len, len(right)))
    return report
