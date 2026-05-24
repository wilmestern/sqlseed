"""Row truncator: trims string values in generated rows to a maximum length."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from sqlseed.schema_parser import TableDefinition


class TruncatorError(Exception):
    """Raised when truncation configuration is invalid."""


@dataclass
class TruncatorConfig:
    """Configuration for the row truncator."""

    global_max_length: Optional[int] = None
    column_limits: Dict[str, int] = field(default_factory=dict)
    ellipsis: str = ""

    def __post_init__(self) -> None:
        if self.global_max_length is not None and self.global_max_length < 1:
            raise TruncatorError("global_max_length must be a positive integer.")
        for col, limit in self.column_limits.items():
            if limit < 1:
                raise TruncatorError(
                    f"Column limit for '{col}' must be a positive integer."
                )
        self.column_limits = {k.lower(): v for k, v in self.column_limits.items()}

    def add_column_limit(self, column: str, max_length: int) -> None:
        """Register a per-column string length limit."""
        if not column:
            raise TruncatorError("Column name must not be empty.")
        if max_length < 1:
            raise TruncatorError("max_length must be a positive integer.")
        self.column_limits[column.lower()] = max_length

    def remove_column_limit(self, column: str) -> None:
        """Remove a per-column limit if present."""
        self.column_limits.pop(column.lower(), None)

    def limit_for(self, column: str) -> Optional[int]:
        """Return the effective limit for *column*, or None if unrestricted."""
        col_limit = self.column_limits.get(column.lower())
        if col_limit is not None:
            return col_limit
        return self.global_max_length


def truncate_value(value: Any, max_length: int, ellipsis: str = "") -> Any:
    """Truncate *value* to *max_length* characters if it is a string."""
    if not isinstance(value, str):
        return value
    if len(value) <= max_length:
        return value
    cut = max_length - len(ellipsis)
    if cut < 0:
        cut = 0
    return value[:cut] + ellipsis


def truncate_row(
    row: Dict[str, Any],
    config: TruncatorConfig,
) -> Dict[str, Any]:
    """Return a new row with string values truncated according to *config*."""
    result: Dict[str, Any] = {}
    for col, value in row.items():
        limit = config.limit_for(col)
        if limit is not None:
            result[col] = truncate_value(value, limit, config.ellipsis)
        else:
            result[col] = value
    return result


def truncate_rows(
    rows: List[Dict[str, Any]],
    config: TruncatorConfig,
) -> List[Dict[str, Any]]:
    """Apply :func:`truncate_row` to every row in *rows*."""
    return [truncate_row(row, config) for row in rows]
