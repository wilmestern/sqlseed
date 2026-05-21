"""Tests for sqlseed.constraint_validator."""

import pytest

from sqlseed.schema_parser import ColumnDefinition, TableDefinition
from sqlseed.constraint_validator import (
    ValidationError,
    ValidationResult,
    UniquenessTracker,
    validate_row,
)


@pytest.fixture
def simple_table() -> TableDefinition:
    return TableDefinition(
        name="users",
        columns=[
            ColumnDefinition(name="id", data_type="INT", nullable=False, primary_key=True),
            ColumnDefinition(name="email", data_type="VARCHAR", nullable=False, unique=True, max_length=100),
            ColumnDefinition(name="bio", data_type="TEXT", nullable=True),
        ],
    )


def test_valid_row_returns_valid_result(simple_table):
    row = {"id": 1, "email": "alice@example.com", "bio": "Hello"}
    result = validate_row(row, simple_table)
    assert result.valid is True
    assert result.errors == []


def test_null_non_nullable_column_fails(simple_table):
    row = {"id": 1, "email": None, "bio": None}
    result = validate_row(row, simple_table)
    assert result.valid is False
    assert any(e.column == "email" for e in result.errors)


def test_nullable_column_allows_none(simple_table):
    row = {"id": 1, "email": "bob@example.com", "bio": None}
    result = validate_row(row, simple_table)
    assert result.valid is True


def test_primary_key_null_is_allowed(simple_table):
    """Primary key columns skip the NOT NULL check (may be DB-generated)."""
    row = {"id": None, "email": "carol@example.com", "bio": None}
    result = validate_row(row, simple_table)
    assert result.valid is True


def test_varchar_exceeds_max_length_fails(simple_table):
    long_email = "a" * 200 + "@example.com"
    row = {"id": 1, "email": long_email, "bio": None}
    result = validate_row(row, simple_table)
    assert result.valid is False
    assert any("max_length" in e.message for e in result.errors)


def test_varchar_within_max_length_passes(simple_table):
    row = {"id": 1, "email": "short@x.com", "bio": None}
    result = validate_row(row, simple_table)
    assert result.valid is True


def test_uniqueness_tracker_detects_duplicate():
    tracker = UniquenessTracker()
    assert tracker.check_and_register("email", "a@b.com") is True
    assert tracker.check_and_register("email", "a@b.com") is False


def test_uniqueness_tracker_different_values_pass():
    tracker = UniquenessTracker()
    assert tracker.check_and_register("email", "a@b.com") is True
    assert tracker.check_and_register("email", "c@d.com") is True


def test_uniqueness_tracker_reset_clears_state():
    tracker = UniquenessTracker()
    tracker.check_and_register("email", "a@b.com")
    tracker.reset()
    assert tracker.check_and_register("email", "a@b.com") is True


def test_unique_column_duplicate_fails_with_tracker(simple_table):
    tracker = UniquenessTracker()
    row = {"id": 1, "email": "dup@example.com", "bio": None}
    result1 = validate_row(row, simple_table, tracker=tracker)
    result2 = validate_row(row, simple_table, tracker=tracker)
    assert result1.valid is True
    assert result2.valid is False
    assert any("UNIQUE" in e.message for e in result2.errors)


def test_validation_result_add_error():
    result = ValidationResult(valid=True)
    result.add_error("col", "some error")
    assert result.valid is False
    assert len(result.errors) == 1
    assert result.errors[0].column == "col"
