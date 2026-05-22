"""Seed generation with before/after row lifecycle hooks applied."""
from typing import Dict, List, Optional

from sqlseed.enriched_generator import generate_enriched_row
from sqlseed.row_hooks import RowHooks, RowDict
from sqlseed.schema_parser import TableDefinition


class HookedGenerationError(Exception):
    """Raised when a hooked row cannot be produced after max retries."""


def generate_hooked_row(
    table: TableDefinition,
    hooks: RowHooks,
    context: Optional[Dict[str, object]] = None,
    max_retries: int = 10,
) -> RowDict:
    """Generate a single row with before/after hooks applied.

    The before-hook runs on an empty dict so hooks can seed initial values.
    The after-hook runs on the generated row for post-processing.
    """
    for attempt in range(max_retries):
        seed: RowDict = hooks.run_before(table.name, {})
        row: RowDict = generate_enriched_row(table, overrides=seed)
        row = hooks.run_after(table.name, row)
        if row is not None:
            return row
        raise HookedGenerationError(
            f"After-hook returned None for table '{table.name}' on attempt {attempt + 1}"
        )
    raise HookedGenerationError(
        f"Could not generate a valid hooked row for '{table.name}' after {max_retries} retries"
    )


def generate_hooked_rows(
    table: TableDefinition,
    count: int,
    hooks: RowHooks,
    context: Optional[Dict[str, object]] = None,
    max_retries: int = 10,
) -> List[RowDict]:
    """Generate *count* rows for *table* with hooks applied to each."""
    return [
        generate_hooked_row(table, hooks, context=context, max_retries=max_retries)
        for _ in range(count)
    ]
