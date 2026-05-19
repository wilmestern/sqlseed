"""Tests for sqlseed.dialect module."""

import pytest
from sqlseed.dialect import (
    Dialect,
    get_dialect,
    format_identifier,
    format_placeholder,
    build_insert_statement,
)


def test_get_dialect_postgres():
    assert get_dialect("postgres") == Dialect.POSTGRES


def test_get_dialect_mysql():
    assert get_dialect("mysql") == Dialect.MYSQL


def test_get_dialect_sqlite():
    assert get_dialect("sqlite") == Dialect.SQLITE


def test_get_dialect_case_insensitive():
    assert get_dialect("POSTGRES") == Dialect.POSTGRES
    assert get_dialect("MySQL") == Dialect.MYSQL


def test_get_dialect_invalid_raises():
    with pytest.raises(ValueError, match="Unsupported dialect"):
        get_dialect("oracle")


def test_format_identifier_postgres():
    assert format_identifier("users", Dialect.POSTGRES) == '"users"'


def test_format_identifier_mysql():
    assert format_identifier("users", Dialect.MYSQL) == "`users`"


def test_format_identifier_sqlite():
    assert format_identifier("users", Dialect.SQLITE) == '"users"'


def test_format_placeholder_postgres():
    assert format_placeholder(1, Dialect.POSTGRES) == "$1"
    assert format_placeholder(3, Dialect.POSTGRES) == "$3"


def test_format_placeholder_mysql():
    assert format_placeholder(1, Dialect.MYSQL) == "%s"


def test_format_placeholder_sqlite():
    assert format_placeholder(1, Dialect.SQLITE) == "?"


def test_build_insert_statement_postgres():
    sql = build_insert_statement(
        "users",
        ["id", "name"],
        ["1", "'Alice'"],
        Dialect.POSTGRES,
    )
    assert sql == 'INSERT INTO "users" ("id", "name") VALUES (1, \'Alice\');'


def test_build_insert_statement_mysql():
    sql = build_insert_statement(
        "users",
        ["id", "email"],
        ["42", "'user@example.com'"],
        Dialect.MYSQL,
    )
    assert sql == "INSERT INTO `users` (`id`, `email`) VALUES (42, 'user@example.com');"


def test_build_insert_statement_with_placeholders_postgres():
    sql = build_insert_statement(
        "orders",
        ["id", "total", "status"],
        ["1", "99.99", "'pending'"],
        Dialect.POSTGRES,
        use_placeholders=True,
    )
    assert sql == 'INSERT INTO "orders" ("id", "total", "status") VALUES ($1, $2, $3);'


def test_build_insert_statement_with_placeholders_sqlite():
    sql = build_insert_statement(
        "items",
        ["a", "b"],
        ["x", "y"],
        Dialect.SQLITE,
        use_placeholders=True,
    )
    assert sql == 'INSERT INTO "items" ("a", "b") VALUES (?, ?);'
