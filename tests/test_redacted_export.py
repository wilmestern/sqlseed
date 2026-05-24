"""Tests for sqlseed.redacted_export."""
import json

import pytest

from sqlseed.redacted_export import export_redacted, generate_redacted_rows
from sqlseed.row_redactor import RedactorConfig
from sqlseed.schema_parser import ColumnDefinition, TableDefinition


@pytest.fixture()
def users_table() -> TableDefinition:
    return TableDefinition(
        name="users",
        columns=[
            ColumnDefinition(name="id", data_type="INTEGER", nullable=False, primary_key=True),
            ColumnDefinition(name="email", data_type="VARCHAR", nullable=False, max_length=255),
            ColumnDefinition(name="password_hash", data_type="VARCHAR", nullable=False, max_length=255),
            ColumnDefinition(name="username", data_type="VARCHAR", nullable=True, max_length=100),
        ],
    )


@pytest.fixture()
def redactor_config() -> RedactorConfig:
    cfg = RedactorConfig(default_mask="[REDACTED]")
    cfg.add("email")
    cfg.add("password_hash")
    return cfg


# ---------------------------------------------------------------------------
# generate_redacted_rows
# ---------------------------------------------------------------------------

def test_generate_redacted_rows_returns_list(users_table, redactor_config):
    rows = generate_redacted_rows(users_table, 5, redactor_config)
    assert isinstance(rows, list)


def test_generate_redacted_rows_correct_count(users_table, redactor_config):
    rows = generate_redacted_rows(users_table, 7, redactor_config)
    assert len(rows) == 7


def test_generate_redacted_rows_each_is_dict(users_table, redactor_config):
    rows = generate_redacted_rows(users_table, 3, redactor_config)
    assert all(isinstance(r, dict) for r in rows)


def test_generate_redacted_rows_sensitive_columns_masked(users_table, redactor_config):
    rows = generate_redacted_rows(users_table, 10, redactor_config)
    for row in rows:
        assert row["email"] == "[REDACTED]"
        assert row["password_hash"] == "[REDACTED]"


def test_generate_redacted_rows_non_sensitive_columns_present(users_table, redactor_config):
    rows = generate_redacted_rows(users_table, 3, redactor_config)
    for row in rows:
        assert "id" in row
        assert "username" in row


def test_generate_redacted_rows_zero_count_returns_empty(users_table, redactor_config):
    rows = generate_redacted_rows(users_table, 0, redactor_config)
    assert rows == []


def test_generate_redacted_rows_no_rules_leaves_values(users_table):
    cfg = RedactorConfig()  # no rules
    rows = generate_redacted_rows(users_table, 3, cfg)
    for row in rows:
        assert row["email"] != "[REDACTED]"


# ---------------------------------------------------------------------------
# export_redacted
# ---------------------------------------------------------------------------

def test_export_redacted_returns_string(users_table, redactor_config):
    result = export_redacted(users_table, 3, redactor_config)
    assert isinstance(result, str)


def test_export_redacted_is_valid_json(users_table, redactor_config):
    result = export_redacted(users_table, 3, redactor_config)
    parsed = json.loads(result)
    assert isinstance(parsed, list)


def test_export_redacted_correct_count(users_table, redactor_config):
    result = export_redacted(users_table, 4, redactor_config)
    parsed = json.loads(result)
    assert len(parsed) == 4


def test_export_redacted_sensitive_columns_masked_in_json(users_table, redactor_config):
    result = export_redacted(users_table, 5, redactor_config)
    parsed = json.loads(result)
    for row in parsed:
        assert row["email"] == "[REDACTED]"
        assert row["password_hash"] == "[REDACTED]"
