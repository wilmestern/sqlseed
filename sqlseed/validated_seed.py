"""High-level helper that generates and validates rows, retrying on constraint violations."""

from typing import Any, Dict, List, Optional

from sqlseed.schema_parser import TableDefinition
from sqlseed.insert_generator import generate_row
from sqlseed.constraint_validator import UniquenessTracker, validate_row, ValidationResult

MAX_RETRIES = 10


class RowGenerationError(Exception):
    """Raised when a valid row cannot be generated within the retry limit."""


def generate_valid_row(
    table: TableDefinition,
    tracker: Optional[UniquenessTracker] = None,
    max_retries: int = MAX_RETRIES,
) -> Dict[str, Any]:
    """Generate a single row that passes all constraint validations.

    Retries up to *max_retries* times if the generated row violates constraints.
    Raises RowGenerationError if no valid row could be produced.
    """
    for attempt in range(max_retries):
        row = generate_row(table)
        result: ValidationResult = validate_row(row, table, tracker=tracker)
        if result.valid:
            return row
    error_summary = "; ".join(
        f"{e.column}: {e.message}" for e in result.errors  # type: ignore[possibly-undefined]
    )
    raise RowGenerationError(
        f"Could not generate a valid row for table '{table.name}' "
        f"after {max_retries} attempts. Last errors: {error_summary}"
    )


def generate_valid_rows(
    table: TableDefinition,
    count: int = 1,
    max_retries: int = MAX_RETRIES,
) -> List[Dict[str, Any]]:
    """Generate *count* validated rows for *table*, respecting UNIQUE constraints across rows."""
    tracker = UniquenessTracker()
    rows: List[Dict[str, Any]] = []
    for _ in range(count):
        row = generate_valid_row(table, tracker=tracker, max_retries=max_retries)
        rows.append(row)
    return rows
