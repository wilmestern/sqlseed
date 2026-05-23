"""Merge two sequences of rows by matching on key columns."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence


@dataclass
class MergeConfig:
    """Configuration for a row merge operation."""

    key_columns: List[str]
    prefer: str = "right"  # 'left' | 'right'
    case_sensitive_keys: bool = False

    def __post_init__(self) -> None:
        if self.prefer not in ("left", "right"):
            raise ValueError("prefer must be 'left' or 'right'")
        if not self.key_columns:
            raise ValueError("key_columns must not be empty")
        if not self.case_sensitive_keys:
            self.key_columns = [c.lower() for c in self.key_columns]


Row = Dict[str, Any]


def _make_key(row: Row, key_columns: List[str], case_sensitive: bool) -> tuple:
    """Build a hashable key from the specified columns of a row."""
    if case_sensitive:
        return tuple(row.get(col) for col in key_columns)
    normalised = {k.lower(): v for k, v in row.items()}
    return tuple(normalised.get(col) for col in key_columns)


def merge_rows(
    left: Sequence[Row],
    right: Sequence[Row],
    config: MergeConfig,
) -> List[Row]:
    """Merge *right* rows into *left* rows on key columns.

    Rows present in both sequences are merged field-by-field; the
    ``prefer`` setting controls which side wins for conflicting values.
    Rows present in only one sequence are included as-is.
    """
    index: Dict[tuple, Row] = {}
    for row in left:
        key = _make_key(row, config.key_columns, config.case_sensitive_keys)
        index[key] = dict(row)

    for row in right:
        key = _make_key(row, config.key_columns, config.case_sensitive_keys)
        if key in index:
            existing = index[key]
            if config.prefer == "right":
                merged = {**existing, **row}
            else:
                merged = {**row, **existing}
            index[key] = merged
        else:
            index[key] = dict(row)

    return list(index.values())


def merge_summary(before: Sequence[Row], after: Sequence[Row]) -> Dict[str, int]:
    """Return a simple summary of how many rows were added, kept, or updated."""
    before_count = len(before)
    after_count = len(after)
    added = max(0, after_count - before_count)
    return {
        "before": before_count,
        "after": after_count,
        "added": added,
        "updated": after_count - added,
    }
