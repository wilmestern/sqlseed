"""Tests for sqlseed.hooked_seed."""
import pytest
from sqlseed.row_hooks import RowHooks
from sqlseed.hooked_seed import generate_hooked_row, generate_hooked_rows, HookedGenerationError
from sqlseed.schema_parser import TableDefinition, ColumnDefinition


@pytest.fixture()
def users_table():
    return TableDefinition(
        name="users",
        columns=[
            ColumnDefinition(name="id", col_type="INTEGER", nullable=False, primary_key=True),
            ColumnDefinition(name="email", col_type="VARCHAR", nullable=False, primary_key=False, max_length=255),
            ColumnDefinition(name="age", col_type="INTEGER", nullable=True, primary_key=False),
        ],
    )


@pytest.fixture()
def hooks():
    return RowHooks()


def test_generate_hooked_row_returns_dict(users_table, hooks):
    row = generate_hooked_row(users_table, hooks)
    assert isinstance(row, dict)


def test_generate_hooked_row_has_all_columns(users_table, hooks):
    row = generate_hooked_row(users_table, hooks)
    for col in users_table.columns:
        assert col.name in row


def test_before_hook_value_appears_in_row(users_table, hooks):
    hooks.before("force_age", lambda t, r: {**r, "age": 42})
    row = generate_hooked_row(users_table, hooks)
    assert row["age"] == 42


def test_after_hook_can_override_generated_value(users_table, hooks):
    hooks.after("override_email", lambda t, r: {**r, "email": "fixed@example.com"})
    row = generate_hooked_row(users_table, hooks)
    assert row["email"] == "fixed@example.com"


def test_generate_hooked_rows_count(users_table, hooks):
    rows = generate_hooked_rows(users_table, 5, hooks)
    assert len(rows) == 5


def test_generate_hooked_rows_each_is_dict(users_table, hooks):
    rows = generate_hooked_rows(users_table, 3, hooks)
    for row in rows:
        assert isinstance(row, dict)


def test_before_hook_receives_table_name(users_table, hooks):
    captured = []
    hooks.before("cap", lambda t, r: captured.append(t) or r)
    generate_hooked_row(users_table, hooks)
    assert captured[0] == "users"


def test_after_hook_receives_table_name(users_table, hooks):
    captured = []
    hooks.after("cap", lambda t, r: captured.append(t) or r)
    generate_hooked_row(users_table, hooks)
    assert captured[0] == "users"


def test_zero_rows_returns_empty_list(users_table, hooks):
    rows = generate_hooked_rows(users_table, 0, hooks)
    assert rows == []
