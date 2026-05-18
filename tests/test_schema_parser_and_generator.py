"""Tests for schema_parser and data_generator modules."""

import pytest

from sqlseed.schema_parser import parse_create_table, parse_column, ColumnDefinition
from sqlseed.data_generator import generate_value


SAMPLE_SQL = """
CREATE TABLE IF NOT EXISTS `users` (
    `id` INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `username` VARCHAR(50) NOT NULL,
    `email` VARCHAR(120) NOT NULL UNIQUE,
    `bio` TEXT,
    `score` FLOAT,
    `is_active` BOOLEAN NOT NULL,
    `created_at` DATETIME NOT NULL
);
"""


def test_parse_create_table_returns_table_definition():
    table = parse_create_table(SAMPLE_SQL)
    assert table is not None
    assert table.name == 'users'


def test_parse_create_table_column_count():
    table = parse_create_table(SAMPLE_SQL)
    assert len(table.columns) == 7


def test_parse_create_table_column_names():
    table = parse_create_table(SAMPLE_SQL)
    names = [c.name for c in table.columns]
    assert 'id' in names
    assert 'email' in names
    assert 'created_at' in names


def test_parse_column_primary_key():
    table = parse_create_table(SAMPLE_SQL)
    id_col = next(c for c in table.columns if c.name == 'id')
    assert id_col.primary_key is True
    assert id_col.nullable is False


def test_parse_column_varchar_max_length():
    table = parse_create_table(SAMPLE_SQL)
    username_col = next(c for c in table.columns if c.name == 'username')
    assert username_col.max_length == 50
    assert username_col.data_type == 'VARCHAR'


def test_parse_column_unique():
    table = parse_create_table(SAMPLE_SQL)
    email_col = next(c for c in table.columns if c.name == 'email')
    assert email_col.unique is True


def test_parse_invalid_sql_returns_none():
    result = parse_create_table("SELECT * FROM users;")
    assert result is None


def test_generate_value_int():
    col = ColumnDefinition(name='age', data_type='INT')
    val = generate_value(col)
    assert isinstance(val, int)
    assert 1 <= val <= 10_000


def test_generate_value_varchar_respects_max_length():
    col = ColumnDefinition(name='code', data_type='VARCHAR', max_length=5)
    val = generate_value(col)
    assert isinstance(val, str)
    assert len(val) <= 5


def test_generate_value_email_hint():
    col = ColumnDefinition(name='email', data_type='VARCHAR', max_length=120)
    val = generate_value(col)
    assert '@' in val


def test_generate_value_boolean():
    col = ColumnDefinition(name='is_active', data_type='BOOLEAN')
    val = generate_value(col)
    assert isinstance(val, bool)


def test_generate_value_datetime():
    col = ColumnDefinition(name='created_at', data_type='DATETIME')
    val = generate_value(col)
    assert isinstance(val, str)
    assert len(val) == 19  # YYYY-MM-DD HH:MM:SS
