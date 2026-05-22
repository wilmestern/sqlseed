"""High-level seed generation with automatic deduplication.

Combines enriched row generation with the row deduplicator to
produce a requested number of unique rows, retrying as needed.
"""

from __future__ import annotations

from typing import Dict, List, Optional

from sqlseed.enriched_generator import generate_enriched_row
from sqlseed.row_deduplicator import DeduplicatorConfig, deduplicate_rows
from sqlseed.schema_parser import TableDefinition


class DeduplicationError(RuntimeError):
    """Raised when unique rows cannot be generated within the attempt limit."""


_DEFAULT_MAX_ATTEMPTS_MULTIPLIER = 10


def generate_deduplicated_rows(
    table: TableDefinition,
    count: int,
    config: Optional[DeduplicatorConfig] = None,
    max_attempts: Optional[int] = None,
) -> List[Dict]:
    """Generate *count* unique rows for *table*.

    Parameters
    ----------
    table:
        The table whose schema drives value generation.
    count:
        Number of unique rows desired.
    config:
        Deduplication configuration (key columns, case sensitivity).
        Defaults to full-row comparison.
    max_attempts:
        Maximum total rows to generate before giving up.
        Defaults to ``count * 10``.

    Raises
    ------
    DeduplicationError
        If *max_attempts* is exhausted before *count* unique rows are found.
    ValueError
        If *count* is not a positive integer.
    """
    if count <= 0:
        raise ValueError(f"count must be a positive integer, got {count}")

    if config is None:
        config = DeduplicatorConfig()

    if max_attempts is None:
        max_attempts = count * _DEFAULT_MAX_ATTEMPTS_MULTIPLIER

    accumulated: List[Dict] = []
    attempts = 0

    while len(accumulated) < count and attempts < max_attempts:
        batch_size = min(count - len(accumulated), max(1, count))
        batch = [generate_enriched_row(table) for _ in range(batch_size)]
        attempts += batch_size
        accumulated = deduplicate_rows(accumulated + batch, config)

    if len(accumulated) < count:
        raise DeduplicationError(
            f"Could only generate {len(accumulated)} unique rows out of "
            f"{count} requested after {attempts} attempts for table "
            f"'{table.name}'."
        )

    return accumulated[:count]
