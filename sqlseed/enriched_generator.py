"""Enriched value generation that combines semantic hints with fallback data generation."""

from typing import Any, Optional

from sqlseed.schema_parser import ColumnDefinition
from sqlseed.semantic_generator import generate_semantic_value
from sqlseed.data_generator import generate_value
from sqlseed.null_policy import NullPolicy, apply_null_policy
from sqlseed.value_overrides import OverrideRegistry


def generate_enriched_value(
    column: ColumnDefinition,
    null_policy: Optional[NullPolicy] = None,
    overrides: Optional[OverrideRegistry] = None,
    table_name: str = "",
) -> Any:
    """Generate a value for *column* using the full enrichment pipeline.

    Resolution order:
    1. Override registry (explicit caller-supplied value).
    2. Null policy (may short-circuit to None for nullable columns).
    3. Semantic generator (column-name / type-affinity hints).
    4. Fallback generic generator.
    """
    # 1. Override registry
    if overrides is not None and overrides.has(table_name, column.name):
        return overrides.get(table_name, column.name)

    # 2. Null policy
    if null_policy is not None:
        null_result = apply_null_policy(column, null_policy)
        if null_result is None and column.nullable:
            return None

    # 3. Semantic generator
    semantic = generate_semantic_value(column)
    if semantic is not None:
        return semantic

    # 4. Fallback
    return generate_value(column)


def generate_enriched_row(
    columns: list[ColumnDefinition],
    null_policy: Optional[NullPolicy] = None,
    overrides: Optional[OverrideRegistry] = None,
    table_name: str = "",
) -> dict[str, Any]:
    """Return a dict mapping column names to generated values for all *columns*."""
    return {
        col.name: generate_enriched_value(
            col,
            null_policy=null_policy,
            overrides=overrides,
            table_name=table_name,
        )
        for col in columns
    }
