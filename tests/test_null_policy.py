"""Tests for sqlseed.null_policy."""

from __future__ import annotations

import pytest

from sqlseed.null_policy import NullPolicy, apply_null_policy, should_be_null
from sqlseed.schema_parser import ColumnDefinition


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _col(name: str, nullable: bool = True) -> ColumnDefinition:
    return ColumnDefinition(
        name=name,
        col_type="VARCHAR",
        nullable=nullable,
        primary_key=False,
        max_length=255,
    )


# ---------------------------------------------------------------------------
# NullPolicy construction
# ---------------------------------------------------------------------------

def test_null_policy_default_probability():
    policy = NullPolicy()
    assert policy.null_probability == 0.15


def test_null_policy_invalid_probability_raises():
    with pytest.raises(ValueError, match="null_probability"):
        NullPolicy(null_probability=1.5)


def test_null_policy_negative_probability_raises():
    with pytest.raises(ValueError):
        NullPolicy(null_probability=-0.1)


# ---------------------------------------------------------------------------
# should_be_null
# ---------------------------------------------------------------------------

def test_non_nullable_column_never_null():
    col = _col("email", nullable=False)
    policy = NullPolicy(null_probability=1.0)  # would always null if nullable
    assert should_be_null(col, policy) is False


def test_force_null_column_always_null():
    col = _col("bio", nullable=False)  # even non-nullable
    policy = NullPolicy(force_null_columns={"bio"})
    assert should_be_null(col, policy) is True


def test_force_value_column_never_null():
    col = _col("bio", nullable=True)
    policy = NullPolicy(null_probability=1.0, force_value_columns={"bio"})
    assert should_be_null(col, policy) is False


def test_nullable_column_null_when_probability_is_one():
    col = _col("bio", nullable=True)
    policy = NullPolicy(null_probability=1.0)
    assert should_be_null(col, policy) is True


def test_nullable_column_not_null_when_probability_is_zero():
    col = _col("bio", nullable=True)
    policy = NullPolicy(null_probability=0.0)
    assert should_be_null(col, policy) is False


def test_should_be_null_uses_default_policy_when_none():
    """Passing None should not raise and should use the default policy."""
    col = _col("note", nullable=False)
    result = should_be_null(col, None)
    assert result is False  # non-nullable → never null regardless


# ---------------------------------------------------------------------------
# apply_null_policy
# ---------------------------------------------------------------------------

def test_apply_null_policy_returns_none_when_force_null():
    col = _col("bio")
    policy = NullPolicy(force_null_columns={"bio"})
    result = apply_null_policy(col, "some value", policy)
    assert result is None


def test_apply_null_policy_returns_value_when_force_value():
    col = _col("bio", nullable=True)
    policy = NullPolicy(null_probability=1.0, force_value_columns={"bio"})
    result = apply_null_policy(col, "hello", policy)
    assert result == "hello"


def test_apply_null_policy_returns_value_for_non_nullable():
    col = _col("username", nullable=False)
    policy = NullPolicy(null_probability=1.0)
    result = apply_null_policy(col, "alice", policy)
    assert result == "alice"


def test_apply_null_policy_returns_none_probability_one():
    col = _col("notes", nullable=True)
    policy = NullPolicy(null_probability=1.0)
    result = apply_null_policy(col, "text", policy)
    assert result is None
