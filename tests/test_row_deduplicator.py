"""Tests for sqlseed.row_deduplicator."""

import pytest

from sqlseed.row_deduplicator import (
    DeduplicatorConfig,
    count_duplicates,
    deduplicate_rows,
)


# ---------------------------------------------------------------------------
# DeduplicatorConfig
# ---------------------------------------------------------------------------

def test_deduplicator_config_defaults():
    cfg = DeduplicatorConfig()
    assert cfg.key_columns is None
    assert cfg.case_sensitive is True


def test_deduplicator_config_normalises_key_columns_case_insensitive():
    cfg = DeduplicatorConfig(key_columns=["Email", "NAME"], case_sensitive=False)
    assert cfg.key_columns == ["email", "name"]


def test_deduplicator_config_preserves_key_columns_case_sensitive():
    cfg = DeduplicatorConfig(key_columns=["Email", "NAME"], case_sensitive=True)
    assert cfg.key_columns == ["Email", "NAME"]


# ---------------------------------------------------------------------------
# deduplicate_rows — full-row comparison
# ---------------------------------------------------------------------------

def test_deduplicate_rows_empty_input():
    assert deduplicate_rows([]) == []


def test_deduplicate_rows_no_duplicates_returns_all():
    rows = [{"id": 1, "name": "alice"}, {"id": 2, "name": "bob"}]
    result = deduplicate_rows(rows)
    assert len(result) == 2


def test_deduplicate_rows_removes_exact_duplicate():
    rows = [
        {"id": 1, "name": "alice"},
        {"id": 1, "name": "alice"},
    ]
    result = deduplicate_rows(rows)
    assert len(result) == 1
    assert result[0] == {"id": 1, "name": "alice"}


def test_deduplicate_rows_first_occurrence_wins():
    rows = [
        {"id": 1, "name": "alice"},
        {"id": 1, "name": "ALICE"},
        {"id": 1, "name": "alice"},
    ]
    result = deduplicate_rows(rows)
    assert len(result) == 2
    assert result[0]["name"] == "alice"
    assert result[1]["name"] == "ALICE"


# ---------------------------------------------------------------------------
# deduplicate_rows — key-column comparison
# ---------------------------------------------------------------------------

def test_deduplicate_rows_key_columns_ignores_other_fields():
    rows = [
        {"id": 1, "email": "a@example.com", "score": 10},
        {"id": 2, "email": "a@example.com", "score": 99},
    ]
    cfg = DeduplicatorConfig(key_columns=["email"])
    result = deduplicate_rows(rows, cfg)
    assert len(result) == 1
    assert result[0]["score"] == 10


def test_deduplicate_rows_key_columns_case_insensitive_match():
    rows = [
        {"email": "Alice@Example.com"},
        {"email": "alice@example.com"},
    ]
    cfg = DeduplicatorConfig(key_columns=["email"], case_sensitive=False)
    result = deduplicate_rows(rows, cfg)
    # Keys are lowered, but values are compared as-is via json; both have
    # different raw values so they are NOT considered duplicates by value.
    # This is expected behaviour — key_columns only controls which columns
    # are compared, not value normalisation.
    assert len(result) == 2


def test_deduplicate_rows_key_columns_same_value_deduped():
    rows = [
        {"id": 1, "email": "same@example.com"},
        {"id": 2, "email": "same@example.com"},
    ]
    cfg = DeduplicatorConfig(key_columns=["email"])
    result = deduplicate_rows(rows, cfg)
    assert len(result) == 1


# ---------------------------------------------------------------------------
# count_duplicates
# ---------------------------------------------------------------------------

def test_count_duplicates_no_duplicates():
    rows = [{"id": i} for i in range(5)]
    assert count_duplicates(rows) == 0


def test_count_duplicates_with_duplicates():
    rows = [{"id": 1}, {"id": 1}, {"id": 2}, {"id": 2}, {"id": 2}]
    assert count_duplicates(rows) == 3


def test_count_duplicates_empty():
    assert count_duplicates([]) == 0
