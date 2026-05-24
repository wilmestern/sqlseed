"""Row redaction: replace sensitive column values with configurable masks."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional


class RedactorError(Exception):
    """Raised when redaction configuration is invalid."""


@dataclass
class RedactorConfig:
    """Configuration for the row redactor."""

    default_mask: str = "***REDACTED***"
    case_sensitive: bool = False
    _rules: Dict[str, Callable[[Any], Any]] = field(default_factory=dict, init=False, repr=False)

    def __post_init__(self) -> None:
        if not self.default_mask:
            raise RedactorError("default_mask must not be empty.")

    def _normalise(self, column: str) -> str:
        return column if self.case_sensitive else column.lower()

    def add(self, column: str, mask: Optional[Callable[[Any], Any]] = None) -> None:
        """Register a redaction rule for *column*.

        If *mask* is None the default_mask string is used.
        If *mask* is callable it receives the original value and returns the replacement.
        """
        if not column or not column.strip():
            raise RedactorError("column name must not be empty.")
        if mask is not None and not callable(mask):
            raise RedactorError("mask must be callable or None.")
        key = self._normalise(column.strip())
        self._rules[key] = mask if mask is not None else lambda _: self.default_mask

    def remove(self, column: str) -> None:
        """Remove the redaction rule for *column* (no-op if absent)."""
        key = self._normalise(column.strip())
        self._rules.pop(key, None)

    def clear(self) -> None:
        """Remove all registered redaction rules."""
        self._rules.clear()

    def names(self) -> List[str]:
        """Return the list of columns currently registered for redaction."""
        return list(self._rules.keys())

    def has(self, column: str) -> bool:
        return self._normalise(column.strip()) in self._rules


def redact_row(row: Dict[str, Any], config: RedactorConfig) -> Dict[str, Any]:
    """Return a new row dict with sensitive columns replaced according to *config*."""
    result: Dict[str, Any] = {}
    for col, value in row.items():
        key = config._normalise(col)
        if key in config._rules:
            result[col] = config._rules[key](value)
        else:
            result[col] = value
    return result


def redact_rows(
    rows: List[Dict[str, Any]], config: RedactorConfig
) -> List[Dict[str, Any]]:
    """Apply redaction to every row in *rows*."""
    return [redact_row(row, config) for row in rows]
