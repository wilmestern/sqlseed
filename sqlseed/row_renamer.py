"""Row column renamer — remap column names in generated rows."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


class RenamerError(Exception):
    """Raised when a renaming operation fails."""


@dataclass
class RenameConfig:
    """Configuration for renaming columns in a row."""

    mapping: Dict[str, str] = field(default_factory=dict)
    case_sensitive: bool = False

    def __post_init__(self) -> None:
        if not self.case_sensitive:
            self.mapping = {k.lower(): v for k, v in self.mapping.items()}

    def add(self, source: str, target: str) -> None:
        """Register a rename from *source* column to *target* name."""
        if not source or not target:
            raise RenamerError("Source and target column names must be non-empty strings.")
        key = source if self.case_sensitive else source.lower()
        self.mapping[key] = target

    def remove(self, source: str) -> None:
        """Remove a rename rule; silently ignored if not present."""
        key = source if self.case_sensitive else source.lower()
        self.mapping.pop(key, None)

    def clear(self) -> None:
        """Remove all rename rules."""
        self.mapping.clear()

    def sources(self) -> List[str]:
        """Return all registered source column names."""
        return list(self.mapping.keys())


def rename_row(row: Dict[str, object], config: RenameConfig) -> Dict[str, object]:
    """Return a new row dict with columns renamed according to *config*."""
    result: Dict[str, object] = {}
    for col, value in row.items():
        lookup_key = col if config.case_sensitive else col.lower()
        new_name = config.mapping.get(lookup_key, col)
        if new_name in result:
            raise RenamerError(
                f"Rename collision: target column '{new_name}' already exists in the output row."
            )
        result[new_name] = value
    return result


def rename_rows(
    rows: List[Dict[str, object]], config: RenameConfig
) -> List[Dict[str, object]]:
    """Apply *rename_row* to every row in *rows*."""
    return [rename_row(row, config) for row in rows]
