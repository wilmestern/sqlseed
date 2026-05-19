"""Tests for sqlseed.insert_generator module."""

import pytest
from sqlseed.schema_parser import parse_create_table
from sqlseed.insert_generator import (
    generate_row,
    generate_insert,
    generate_inserts,
    generate_seed_script,
    _format_value,
)

CREATE_USERS = """
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL,
    created_at DATETIME,
    is_active BOOLEAN DEFAULT TRUE
)
"""

CREATE_POSTS = """
CREATE TABLE posts (
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(200) NOT NULL,
    body TEXT,
    published_at DATE
)
"""


@pytest.fixture
def users_table():
    return parse_create_table(CREATE_USERS)


@pytest.fixture
def posts_table():
    return parse_create_table(CREATE_POSTS)


def test_format_value_none():
    assert _format_value(None) == "NULL"


def test_format_value_integer():
    assert _format_value(42) == "42"


def test_format_value_string():
    assert _format_value("hello") == "'hello'"


def test_format_value_string_escapes_quotes():
    assert _format_value("it's") == "'it''s'"


def test_format_value_bool_true():
    assert _format_value(True) == "1"


def test_format_value_bool_false():
    assert _format_value(False) == "0"


def test_generate_row_has_all_columns(users_table):
    row = generate_row(users_table)
    column_names = {col.name for col in users_table.columns}
    assert set(row.keys()) == column_names


def test_generate_insert_returns_string(users_table):
    stmt = generate_insert(users_table)
    assert isinstance(stmt, str)


def test_generate_insert_starts_with_insert_into(users_table):
    stmt = generate_insert(users_table)
    assert stmt.startswith("INSERT INTO users")


def test_generate_insert_ends_with_semicolon(users_table):
    stmt = generate_insert(users_table)
    assert stmt.endswith(";")


def test_generate_insert_uses_provided_row(users_table):
    row = {col.name: None for col in users_table.columns}
    stmt = generate_insert(users_table, row=row)
    assert "NULL" in stmt


def test_generate_inserts_count(users_table):
    stmts = generate_inserts(users_table, count=5)
    assert len(stmts) == 5


def test_generate_inserts_with_rows(users_table):
    rows = [generate_row(users_table) for _ in range(3)]
    stmts = generate_inserts(users_table, rows=rows)
    assert len(stmts) == 3


def test_generate_seed_script_contains_table_names(users_table, posts_table):
    script = generate_seed_script([users_table, posts_table], count=2)
    assert "users" in script
    assert "posts" in script


def test_generate_seed_script_row_count(users_table):
    script = generate_seed_script([users_table], count=3)
    assert script.count("INSERT INTO users") == 3
