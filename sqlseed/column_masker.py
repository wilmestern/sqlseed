"""Column masking: redact or anonymize sensitive column values in generated rows."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional


@dataclass
class ColumnMasker:
    """Registry of masking functions applied to specific columns before output."""

    _masks: Dict[str, Callable[[Any], Any]] = field(default_factory=dict, init=False)

    def add(self, column_name: str, mask_fn: Callable[[Any], Any]) -> None:
        """Register a masking function for *column_name* (case-insensitive)."""
        if not callable(mask_fn):
            raise TypeError(f"mask_fn for '{column_name}' must be callable, got {type(mask_fn).__name__}")
        self._masks[column_name.lower()] = mask_fn

    def remove(self, column_name: str) -> None:
        """Unregister the masking function for *column_name*. No-op if absent."""
        self._masks.pop(column_name.lower(), None)

    def clear(self) -> None:
        """Remove all registered masking functions."""
        self._masks.clear()

    def names(self) -> list[str]:
        """Return the names of all masked columns."""
        return list(self._masks.keys())

    def is_masked(self, column_name: str) -> bool:
        """Return True if *column_name* has a registered mask."""
        return column_name.lower() in self._masks

    def apply(self, column_name: str, value: Any) -> Any:
        """Apply the mask for *column_name* to *value*, or return *value* unchanged."""
        fn = self._masks.get(column_name.lower())
        return fn(value) if fn is not None else value

    def mask_row(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """Return a new dict with all registered masks applied to matching keys."""
        return {col: self.apply(col, val) for col, val in row.items()}


# ---------------------------------------------------------------------------
# Built-in convenience mask factories
# ---------------------------------------------------------------------------

def redact(placeholder: str = "***") -> Callable[[Any], str]:
    """Return a mask that replaces any value with *placeholder*."""
    def _mask(_value: Any) -> str:
        return placeholder
    return _mask


def partial_mask(visible_chars: int = 4, mask_char: str = "*") -> Callable[[Any], str]:
    """Return a mask that keeps the first *visible_chars* characters and masks the rest."""
    def _mask(value: Any) -> str:
        s = str(value) if value is not None else ""
        if len(s) <= visible_chars:
            return s
        return s[:visible_chars] + mask_char * (len(s) - visible_chars)
    return _mask


def hash_mask() -> Callable[[Any], str]:
    """Return a mask that replaces the value with a hex digest of its string repr."""
    import hashlib

    def _mask(value: Any) -> str:
        return hashlib.sha256(str(value).encode()).hexdigest()[:16]
    return _mask
