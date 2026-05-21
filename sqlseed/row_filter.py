"""Row filter module for sqlseed.

Provides predicate-based filtering of generated rows before they are
written to the output, allowing callers to exclude rows that do not
meet domain-specific conditions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Any

Row = Dict[str, Any]
Predicate = Callable[[Row], bool]


@dataclass
class RowFilter:
    """Holds a collection of named predicates applied to generated rows."""

    _predicates: List[tuple[str, Predicate]] = field(default_factory=list)

    def add(self, name: str, predicate: Predicate) -> None:
        """Register a named predicate."""
        self._predicates.append((name, predicate))

    def remove(self, name: str) -> None:
        """Remove a predicate by name. Silently ignores unknown names."""
        self._predicates = [(n, p) for n, p in self._predicates if n != name]

    def clear(self) -> None:
        """Remove all registered predicates."""
        self._predicates.clear()

    def names(self) -> List[str]:
        """Return the names of all registered predicates."""
        return [n for n, _ in self._predicates]

    def passes(self, row: Row) -> bool:
        """Return True only if the row satisfies every registered predicate."""
        return all(predicate(row) for _, predicate in self._predicates)

    def apply(self, rows: List[Row]) -> List[Row]:
        """Return only the rows that satisfy all predicates."""
        return [row for row in rows if self.passes(row)]


def filter_rows(rows: List[Row], predicates: List[Predicate]) -> List[Row]:
    """Functional helper: filter *rows* using an ad-hoc list of predicates.

    Each predicate must return True for a row to be kept.
    """
    result: List[Row] = []
    for row in rows:
        if all(p(row) for p in predicates):
            result.append(row)
    return result
