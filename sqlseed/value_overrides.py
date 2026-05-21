"""Value overrides allow callers to pin specific column values during seed generation.

This is useful when you want deterministic values for certain columns (e.g. a known
user ID, a fixed email address) while letting the generator fill in the rest.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Tuple


# Key: (table_name, column_name) -> pinned value
_OverrideMap = Dict[Tuple[str, str], Any]


@dataclass
class OverrideRegistry:
    """Holds column-level value overrides keyed by (table, column)."""

    _overrides: _OverrideMap = field(default_factory=dict)

    def set(self, table: str, column: str, value: Any) -> None:
        """Pin *value* for *column* in *table*."""
        if not table:
            raise ValueError("table name must not be empty")
        if not column:
            raise ValueError("column name must not be empty")
        self._overrides[(table.lower(), column.lower())] = value

    def get(self, table: str, column: str) -> Optional[Any]:
        """Return the pinned value, or *None* if no override is registered."""
        return self._overrides.get((table.lower(), column.lower()))

    def has(self, table: str, column: str) -> bool:
        """Return *True* when an explicit override exists (even if the value is None)."""
        return (table.lower(), column.lower()) in self._overrides

    def clear(self, table: Optional[str] = None) -> None:
        """Remove overrides.  If *table* is given, only that table's entries are cleared."""
        if table is None:
            self._overrides.clear()
        else:
            keys_to_remove = [k for k in self._overrides if k[0] == table.lower()]
            for k in keys_to_remove:
                del self._overrides[k]

    def all_for_table(self, table: str) -> Dict[str, Any]:
        """Return a plain dict of {column: value} for every override registered for *table*."""
        prefix = table.lower()
        return {col: val for (tbl, col), val in self._overrides.items() if tbl == prefix}


def apply_overrides(row: Dict[str, Any], table: str, registry: OverrideRegistry) -> Dict[str, Any]:
    """Return a copy of *row* with any registered overrides applied."""
    result = dict(row)
    for column, value in registry.all_for_table(table).items():
        # Match case-insensitively against actual row keys
        for key in list(result.keys()):
            if key.lower() == column:
                result[key] = value
                break
    return result
