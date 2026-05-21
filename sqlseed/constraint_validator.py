"""Validates generated row data against table constraints (NOT NULL, UNIQUE, CHECK basics)."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set

from sqlseed.schema_parser import TableDefinition


@dataclass
class ValidationError:
    column: str
    message: str


@dataclass
class ValidationResult:
    valid: bool
    errors: List[ValidationError] = field(default_factory=list)

    def add_error(self, column: str, message: str) -> None:
        self.errors.append(ValidationError(column=column, message=message))
        self.valid = False


@dataclass
class UniquenessTracker:
    """Tracks previously seen values per column to enforce UNIQUE constraints."""
    _seen: Dict[str, Set[Any]] = field(default_factory=dict)

    def check_and_register(self, column: str, value: Any) -> bool:
        """Returns True if value is unique for the column, False if duplicate."""
        if column not in self._seen:
            self._seen[column] = set()
        if value in self._seen[column]:
            return False
        self._seen[column].add(value)
        return True

    def reset(self) -> None:
        self._seen.clear()


def validate_row(
    row: Dict[str, Any],
    table: TableDefinition,
    tracker: Optional[UniquenessTracker] = None,
) -> ValidationResult:
    """Validate a single generated row against the table's column constraints."""
    result = ValidationResult(valid=True)

    for col in table.columns:
        value = row.get(col.name)

        # NOT NULL check (skip primary keys — they may be auto-generated)
        if not col.nullable and not col.primary_key and value is None:
            result.add_error(col.name, f"Column '{col.name}' is NOT NULL but value is None")

        # UNIQUE check
        if col.unique and tracker is not None:
            if value is not None and not tracker.check_and_register(col.name, value):
                result.add_error(
                    col.name,
                    f"Column '{col.name}' has UNIQUE constraint but duplicate value: {value!r}",
                )

        # VARCHAR max length check
        if col.data_type.upper().startswith("VARCHAR") and isinstance(value, str):
            if col.max_length is not None and len(value) > col.max_length:
                result.add_error(
                    col.name,
                    f"Column '{col.name}' value length {len(value)} exceeds max_length {col.max_length}",
                )

    return result
