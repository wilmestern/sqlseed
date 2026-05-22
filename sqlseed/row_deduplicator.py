"""Row deduplication utility for generated seed data.

Provides hashing and filtering of duplicate rows based on
configurable key columns or full-row comparison.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Set

from sqlseed.schema_parser import TableDefinition


@dataclass
class DeduplicatorConfig:
    """Configuration for row deduplication."""

    key_columns: Optional[List[str]] = None  # None means use all columns
    case_sensitive: bool = True

    def __post_init__(self) -> None:
        if self.key_columns is not None:
            self.key_columns = [
                c if self.case_sensitive else c.lower()
                for c in self.key_columns
            ]


def _row_fingerprint(
    row: Dict,
    key_columns: Optional[List[str]],
    case_sensitive: bool,
) -> str:
    """Compute a stable hash fingerprint for a row."""
    if key_columns is not None:
        if case_sensitive:
            subset = {k: row.get(k) for k in key_columns}
        else:
            lower_row = {k.lower(): v for k, v in row.items()}
            subset = {k: lower_row.get(k) for k in key_columns}
    else:
        subset = row

    serialized = json.dumps(subset, sort_keys=True, default=str)
    return hashlib.sha256(serialized.encode()).hexdigest()


def deduplicate_rows(
    rows: Iterable[Dict],
    config: Optional[DeduplicatorConfig] = None,
) -> List[Dict]:
    """Return a list of rows with duplicates removed (first occurrence wins)."""
    if config is None:
        config = DeduplicatorConfig()

    seen: Set[str] = set()
    result: List[Dict] = []

    for row in rows:
        fp = _row_fingerprint(row, config.key_columns, config.case_sensitive)
        if fp not in seen:
            seen.add(fp)
            result.append(row)

    return result


def count_duplicates(
    rows: Iterable[Dict],
    config: Optional[DeduplicatorConfig] = None,
) -> int:
    """Return the number of duplicate rows that would be removed."""
    rows_list = list(rows)
    deduped = deduplicate_rows(rows_list, config)
    return len(rows_list) - len(deduped)
