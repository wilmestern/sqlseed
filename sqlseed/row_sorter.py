"""Row sorting utilities for ordering generated or exported rows."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, List, Optional


@dataclass
class SortKey:
    """Defines a single sort criterion."""

    column: str
    ascending: bool = True
    key_fn: Optional[Callable[[Any], Any]] = None

    def __post_init__(self) -> None:
        self.column = self.column.strip()
        if not self.column:
            raise ValueError("SortKey column must not be empty.")


@dataclass
class RowSorter:
    """Sorts rows by one or more columns with optional custom key functions."""

    _keys: List[SortKey] = field(default_factory=list, init=False)

    def add(self, column: str, ascending: bool = True,
            key_fn: Optional[Callable[[Any], Any]] = None) -> None:
        """Register a sort key. Keys are applied in registration order."""
        self._keys.append(SortKey(column=column, ascending=ascending, key_fn=key_fn))

    def remove(self, column: str) -> None:
        """Remove a sort key by column name (case-insensitive). No-op if absent."""
        col = column.lower()
        self._keys = [k for k in self._keys if k.column.lower() != col]

    def clear(self) -> None:
        """Remove all registered sort keys."""
        self._keys.clear()

    @property
    def columns(self) -> List[str]:
        """Return column names for all registered sort keys in order."""
        return [k.column for k in self._keys]

    def sort(self, rows: List[dict]) -> List[dict]:
        """Return a new list of rows sorted by all registered keys."""
        if not rows or not self._keys:
            return list(rows)

        result = list(rows)
        # Apply keys in reverse order so the first key has highest priority.
        for key in reversed(self._keys):
            col = key.column

            def _make_keyfn(c: str, fn: Optional[Callable[[Any], Any]]):
                def _keyfn(row: dict) -> Any:
                    val = row.get(c)
                    if fn is not None:
                        return fn(val)
                    # Push None values to the end regardless of direction.
                    return (val is None, val if val is not None else "")
                return _keyfn

            result.sort(
                key=_make_keyfn(col, key.key_fn),
                reverse=not key.ascending,
            )

        return result


def sort_rows(
    rows: List[dict],
    column: str,
    ascending: bool = True,
    key_fn: Optional[Callable[[Any], Any]] = None,
) -> List[dict]:
    """Convenience function to sort rows by a single column."""
    sorter = RowSorter()
    sorter.add(column, ascending=ascending, key_fn=key_fn)
    return sorter.sort(rows)
