"""row_flattener.py — Flatten nested dict values in generated rows into dot-notation keys.

Useful when rows contain JSON-column values that have been deserialized into dicts,
or when downstream consumers expect a flat key/value structure.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


class FlattenerError(Exception):
    """Raised when flattening fails due to configuration or data issues."""


@dataclass
class FlattenerConfig:
    separator: str = "."
    max_depth: int = 5
    skip_columns: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.separator:
            raise FlattenerError("separator must be a non-empty string")
        if self.max_depth < 1:
            raise FlattenerError("max_depth must be at least 1")
        self.skip_columns = [c.lower() for c in self.skip_columns]


def _flatten_value(
    prefix: str,
    value: Any,
    separator: str,
    depth: int,
    max_depth: int,
    out: dict[str, Any],
) -> None:
    if isinstance(value, dict) and depth < max_depth:
        for k, v in value.items():
            child_key = f"{prefix}{separator}{k}" if prefix else str(k)
            _flatten_value(child_key, v, separator, depth + 1, max_depth, out)
    else:
        out[prefix] = value


def flatten_row(row: dict[str, Any], config: FlattenerConfig | None = None) -> dict[str, Any]:
    """Return a new row with nested dict values expanded using dot-notation keys."""
    if config is None:
        config = FlattenerConfig()
    result: dict[str, Any] = {}
    for col, val in row.items():
        if col.lower() in config.skip_columns or not isinstance(val, dict):
            result[col] = val
        else:
            _flatten_value(col, val, config.separator, depth=1, max_depth=config.max_depth, out=result)
    return result


def flatten_rows(
    rows: list[dict[str, Any]],
    config: FlattenerConfig | None = None,
) -> list[dict[str, Any]]:
    """Flatten a list of rows, applying the same config to each."""
    if config is None:
        config = FlattenerConfig()
    return [flatten_row(row, config) for row in rows]
