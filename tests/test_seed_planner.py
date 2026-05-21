"""Tests for the seed_planner module."""

import pytest
from sqlseed.seed_planner import build_fk_map, plan_seed
from sqlseed.schema_parser import parse_create_table
from sqlseed.foreign_key_resolver import ForeignKeyConstraint


USERS_DDL = """
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    name VARCHAR(100)
);
"""

POSTS_DDL = """
CREATE TABLE posts (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    title VARCHAR(200),
    FOREIGN KEY (user_id) REFERENCES users(id)
);
"""


def test_build_fk_map_detects_foreign_key():
    tables = [parse_create_table(USERS_DDL), parse_create_table(POSTS_DDL)]
    ddl_map = {"users": USERS_DDL, "posts": POSTS_DDL}
    fk_map = build_fk_map(tables, ddl_map)
    assert "posts" in fk_map
    assert len(fk_map["posts"]) == 1


def test_build_fk_map_no_fk_table_excluded():
    tables = [parse_create_table(USERS_DDL), parse_create_table(POSTS_DDL)]
    ddl_map = {"users": USERS_DDL, "posts": POSTS_DDL}
    fk_map = build_fk_map(tables, ddl_map)
    assert "users" not in fk_map


def test_build_fk_map_sets_from_table():
    tables = [parse_create_table(POSTS_DDL)]
    ddl_map = {"posts": POSTS_DDL}
    fk_map = build_fk_map(tables, ddl_map)
    assert fk_map["posts"][0].from_table == "posts"


def test_plan_seed_returns_string():
    result = plan_seed([USERS_DDL, POSTS_DDL], row_count=2)
    assert isinstance(result, str)


def test_plan_seed_contains_insert_for_each_table():
    result = plan_seed([USERS_DDL, POSTS_DDL], row_count=2)
    assert "INSERT INTO" in result
    assert "users" in result
    assert "posts" in result


def test_plan_seed_users_before_posts():
    result = plan_seed([POSTS_DDL, USERS_DDL], row_count=1)
    users_pos = result.index("users")
    posts_pos = result.index("posts")
    assert users_pos < posts_pos


def test_plan_seed_respects_row_count():
    result = plan_seed([USERS_DDL], row_count=3)
    insert_count = result.count("INSERT INTO")
    assert insert_count == 3


def test_plan_seed_accepts_dialect_param():
    result = plan_seed([USERS_DDL], row_count=1, dialect="mysql")
    assert isinstance(result, str)
    assert len(result) > 0
