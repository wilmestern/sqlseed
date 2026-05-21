"""Tests for the foreign_key_resolver module."""

import pytest
from sqlseed.foreign_key_resolver import (
    ForeignKeyConstraint,
    ResolutionContext,
    parse_foreign_keys,
    resolve_table_order,
)
from sqlseed.schema_parser import TableDefinition, ColumnDefinition


USERS_DDL = """
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100)
);
"""

POSTS_DDL = """
CREATE TABLE posts (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
"""

COMMENTS_DDL = """
CREATE TABLE comments (
    id INTEGER PRIMARY KEY,
    post_id INTEGER,
    FOREIGN KEY (post_id) REFERENCES posts(id)
);
"""


def test_parse_foreign_keys_returns_list():
    result = parse_foreign_keys(POSTS_DDL)
    assert isinstance(result, list)
    assert len(result) == 1


def test_parse_foreign_keys_correct_columns():
    result = parse_foreign_keys(POSTS_DDL)
    fk = result[0]
    assert fk.from_column == "user_id"
    assert fk.to_table == "users"
    assert fk.to_column == "id"


def test_parse_foreign_keys_no_fk():
    result = parse_foreign_keys(USERS_DDL)
    assert result == []


def test_resolution_context_register_and_lookup():
    ctx = ResolutionContext()
    ctx.register("users", "id", 1)
    ctx.register("users", "id", 2)
    values = ctx.lookup("users", "id")
    assert values == [1, 2]


def test_resolution_context_lookup_missing_returns_none():
    ctx = ResolutionContext()
    assert ctx.lookup("nonexistent", "id") is None


def _make_table(name: str) -> TableDefinition:
    return TableDefinition(name=name, columns=[])


def test_resolve_table_order_no_fks():
    tables = [_make_table("users"), _make_table("posts")]
    order = resolve_table_order(tables, {})
    assert set(order) == {"users", "posts"}


def test_resolve_table_order_respects_dependency():
    tables = [_make_table("posts"), _make_table("users")]
    fk_map = {
        "posts": [ForeignKeyConstraint("posts", "user_id", "users", "id")]
    }
    order = resolve_table_order(tables, fk_map)
    assert order.index("users") < order.index("posts")


def test_resolve_table_order_chained_dependencies():
    tables = [_make_table("comments"), _make_table("posts"), _make_table("users")]
    fk_map = {
        "posts": [ForeignKeyConstraint("posts", "user_id", "users", "id")],
        "comments": [ForeignKeyConstraint("comments", "post_id", "posts", "id")],
    }
    order = resolve_table_order(tables, fk_map)
    assert order.index("users") < order.index("posts")
    assert order.index("posts") < order.index("comments")
