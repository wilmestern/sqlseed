"""Row transformer — apply post-generation transformations to generated rows."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from sqlseed.schema_parser import TableDefinition

TransformFn = Callable[[str, Any, Dict[str, Any]], Any]


@dataclass
class RowTransformer:
    """Registry of named transform functions applied to generated rows."""

    _transforms: Dict[str, TransformFn] = field(default_factory=dict)

    def add(self, name: str, fn: TransformFn) -> None:
        """Register a transform under *name*."""
        if not callable(fn):
            raise TypeError(f"Transform '{name}' must be callable.")
        self._transforms[name] = fn

    def remove(self, name: str) -> None:
        """Remove a transform by name; no-op if absent."""
        self._transforms.pop(name, None)

    def clear(self) -> None:
        """Remove all registered transforms."""
        self._transforms.clear()

    def names(self) -> List[str]:
        """Return names of all registered transforms."""
        return list(self._transforms.keys())

    def apply(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """Return a new row with every registered transform applied in insertion order."""
        result = dict(row)
        for fn in self._transforms.values():
            result = {
                col: fn(col, val, result)
                for col, val in result.items()
            }
        return result


def transform_rows(
    rows: List[Dict[str, Any]],
    transformer: RowTransformer,
) -> List[Dict[str, Any]]:
    """Apply *transformer* to every row in *rows* and return the transformed list."""
    return [transformer.apply(row) for row in rows]


def uppercase_strings(
    column: str, value: Any, row: Dict[str, Any]
) -> Any:
    """Built-in helper: upper-case any string value."""
    if isinstance(value, str):
        return value.upper()
    return value


def mask_column(
    target_column: str,
    mask: str = "***",
) -> TransformFn:
    """Return a transform that replaces *target_column* values with *mask*."""
    def _transform(column: str, value: Any, row: Dict[str, Any]) -> Any:
        if column.lower() == target_column.lower() and value is not None:
            return mask
        return value
    return _transform
