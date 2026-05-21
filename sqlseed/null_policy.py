"""Null policy engine: decides whether a column value should be NULL based on
nullability rules and an optional probability weight."""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Optional

from sqlseed.schema_parser import ColumnDefinition


@dataclass
class NullPolicy:
    """Controls how aggressively nullable columns are set to NULL.

    Attributes:
        null_probability: Probability (0.0–1.0) that a nullable column receives
            NULL instead of a generated value.  Defaults to 0.15 (15 %).
        force_null_columns: Explicit set of column names that should *always*
            be NULL (regardless of nullability flag).
        force_value_columns: Explicit set of column names that should *never*
            be NULL even when the column is nullable.
    """

    null_probability: float = 0.15
    force_null_columns: set[str] = field(default_factory=set)
    force_value_columns: set[str] = field(default_factory=set)

    def __post_init__(self) -> None:
        if not 0.0 <= self.null_probability <= 1.0:
            raise ValueError(
                f"null_probability must be between 0.0 and 1.0, got {self.null_probability}"
            )


def should_be_null(column: ColumnDefinition, policy: Optional[NullPolicy] = None) -> bool:
    """Return True if the column value should be NULL for this row.

    Decision logic (in priority order):
    1. Columns in *force_null_columns* → always NULL.
    2. Columns in *force_value_columns* → never NULL.
    3. Non-nullable columns → never NULL.
    4. Nullable columns → NULL with probability *null_probability*.

    Args:
        column: The column definition being evaluated.
        policy: The active NullPolicy.  If None a default policy is used.

    Returns:
        True when the value should be NULL, False otherwise.
    """
    if policy is None:
        policy = NullPolicy()

    if column.name in policy.force_null_columns:
        return True

    if column.name in policy.force_value_columns:
        return False

    if not column.nullable:
        return False

    return random.random() < policy.null_probability


def apply_null_policy(
    column: ColumnDefinition,
    generated_value: object,
    policy: Optional[NullPolicy] = None,
) -> object:
    """Return NULL (None) or the generated value based on the null policy.

    Args:
        column: The column definition.
        generated_value: The value produced by the data generator.
        policy: The active NullPolicy.

    Returns:
        None if the policy determines the column should be NULL, otherwise
        the original *generated_value*.
    """
    if should_be_null(column, policy):
        return None
    return generated_value
