"""Group generated rows by one or more column values."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class GrouperConfig:
    """Configuration for row grouping behaviour."""

    key_columns: List[str]
    case_sensitive: bool = False

    def __post_init__(self) -> None:
        if not self.key_columns:
            raise ValueError("key_columns must contain at least one column name")
        if not self.case_sensitive:
            self.key_columns = [c.lower() for c in self.key_columns]


def _make_key(
    row: Dict[str, Any], key_columns: List[str], case_sensitive: bool
) -> Tuple[Any, ...]:
    """Build a hashable group key from the specified columns."""
    result = []
    for col in key_columns:
        lookup = col if case_sensitive else col.lower()
        matched = None
        for k, v in row.items():
            candidate = k if case_sensitive else k.lower()
            if candidate == lookup:
                matched = v
                break
        result.append(matched)
    return tuple(result)


def group_rows(
    rows: List[Dict[str, Any]], config: GrouperConfig
) -> Dict[Tuple[Any, ...], List[Dict[str, Any]]]:
    """Partition *rows* into groups keyed by *config.key_columns*."""
    groups: Dict[Tuple[Any, ...], List[Dict[str, Any]]] = defaultdict(list)
    for row in rows:
        key = _make_key(row, config.key_columns, config.case_sensitive)
        groups[key].append(row)
    return dict(groups)


def group_sizes(
    groups: Dict[Tuple[Any, ...], List[Dict[str, Any]]]
) -> Dict[Tuple[Any, ...], int]:
    """Return a mapping of group key → number of rows in that group."""
    return {k: len(v) for k, v in groups.items()}


def largest_group(
    groups: Dict[Tuple[Any, ...], List[Dict[str, Any]]]
) -> Optional[Tuple[Tuple[Any, ...], List[Dict[str, Any]]]]:
    """Return the (key, rows) pair for the group with the most rows, or None."""
    if not groups:
        return None
    key = max(groups, key=lambda k: len(groups[k]))
    return key, groups[key]


def filter_group(
    groups: Dict[Tuple[Any, ...], List[Dict[str, Any]]],
    key: Tuple[Any, ...],
) -> List[Dict[str, Any]]:
    """Return rows for *key*, or an empty list if the key is absent."""
    return groups.get(key, [])
