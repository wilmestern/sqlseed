"""Enriched row generator combining semantic hints, null policy, and value overrides."""
from typing import Any, Dict, Optional

from sqlseed.schema_parser import TableDefinition, ColumnDefinition
from sqlseed.semantic_generator import generate_semantic_value
from sqlseed.column_type_affinity import get_affinity, get_semantic_hint
from sqlseed.null_policy import NullPolicy, apply_null_policy
from sqlseed.value_overrides import OverrideRegistry
from sqlseed.data_generator import generate_value

_default_policy = NullPolicy()
_default_registry = OverrideRegistry()


def generate_enriched_value(
    table_name: str,
    col: ColumnDefinition,
    policy: Optional[NullPolicy] = None,
    registry: Optional[OverrideRegistry] = None,
) -> Any:
    """Generate a single enriched value for *col* in *table_name*.

    Resolution order:
    1. Override registry
    2. Null policy
    3. Semantic generator (if hint found)
    4. Type-affinity-based generator
    """
    pol = policy or _default_policy
    reg = registry or _default_registry

    if reg.has(table_name, col.name):
        override = reg.get(table_name, col.name)
        return override() if callable(override) else override

    if apply_null_policy(col, pol):
        return None

    hint = get_semantic_hint(col.name)
    if hint:
        return generate_semantic_value(col, hint)

    affinity = get_affinity(col.col_type)
    return generate_value(col.col_type, col.max_length)


def generate_enriched_row(
    table: TableDefinition,
    policy: Optional[NullPolicy] = None,
    registry: Optional[OverrideRegistry] = None,
    overrides: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Generate a full row dict for *table* with enriched values.

    *overrides* is a plain dict that takes highest precedence (used by hooks).
    """
    row: Dict[str, Any] = {}
    for col in table.columns:
        if overrides and col.name in overrides:
            row[col.name] = overrides[col.name]
        else:
            row[col.name] = generate_enriched_value(
                table.name, col, policy=policy, registry=registry
            )
    return row
