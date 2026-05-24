"""Row normalizer: apply normalization rules to row field values."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional


class NormalizerError(Exception):
    """Raised when normalization configuration or execution fails."""


@dataclass
class NormalizerConfig:
    """Configuration for row normalization."""

    strip_strings: bool = True
    lowercase_strings: bool = False
    none_for_empty_strings: bool = False
    _column_rules: Dict[str, Callable[[Any], Any]] = field(default_factory=dict, init=False, repr=False)

    def add(self, column: str, fn: Callable[[Any], Any]) -> None:
        """Register a per-column normalization callable."""
        if not column or not column.strip():
            raise NormalizerError("Column name must not be empty.")
        if not callable(fn):
            raise NormalizerError(f"Normalization rule for '{column}' must be callable.")
        self._column_rules[column.lower()] = fn

    def remove(self, column: str) -> None:
        """Remove a per-column normalization rule (no-op if not registered)."""
        self._column_rules.pop(column.lower(), None)

    def columns(self) -> List[str]:
        """Return names of columns with explicit rules."""
        return list(self._column_rules.keys())


def _apply_global(value: Any, config: NormalizerConfig) -> Any:
    """Apply global string normalization rules."""
    if not isinstance(value, str):
        return value
    if config.strip_strings:
        value = value.strip()
    if config.lowercase_strings:
        value = value.lower()
    if config.none_for_empty_strings and value == "":
        return None
    return value


def normalize_row(row: Dict[str, Any], config: NormalizerConfig) -> Dict[str, Any]:
    """Return a new row with normalization rules applied."""
    result: Dict[str, Any] = {}
    for key, value in row.items():
        normalized = _apply_global(value, config)
        col_key = key.lower()
        if col_key in config._column_rules:
            try:
                normalized = config._column_rules[col_key](normalized)
            except Exception as exc:
                raise NormalizerError(
                    f"Normalization rule for column '{key}' raised an error: {exc}"
                ) from exc
        result[key] = normalized
    return result


def normalize_rows(
    rows: List[Dict[str, Any]],
    config: Optional[NormalizerConfig] = None,
) -> List[Dict[str, Any]]:
    """Apply normalization to a list of rows."""
    if config is None:
        config = NormalizerConfig()
    return [normalize_row(row, config) for row in rows]
