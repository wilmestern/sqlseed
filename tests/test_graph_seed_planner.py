"""Tests for sqlseed.graph_seed_planner."""

import pytest

from sqlseed.schema_parser import TableDefinition, ColumnDefinition
from sqlseed.graph_seed_planner import plan_ordered_seed, get_insertion_order


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def users_table():
    return TableDefinition(
        name="users",
        columns=[
            ColumnDefinition(name="id", col_type="INT", nullable=False, primary_key=True),
            ColumnDefinition(name="username", col_type="VARCHAR", nullable=False, max_length=50),
            ColumnDefinition(name="email", col_type="VARCHAR", nullable=False, max_length=100),
        ],
        foreign_keys=[],
    )


@pytest.fixture()
def posts_table():
    return TableDefinition(
        name="posts",
        columns=[
            ColumnDefinition(name="id", col_type="INT", nullable=False, primary_key=True),
            ColumnDefinition(name="user_id", col_type="INT", nullable=False),
            ColumnDefinition(name="title", col_type="VARCHAR", nullable=False, max_length=200),
        ],
        foreign_keys=[("user_id", "users", "id")],
    )


# ---------------------------------------------------------------------------
# get_insertion_order
# ---------------------------------------------------------------------------

def test_insertion_order_users_before_posts(users_table, posts_table):
    order = get_insertion_order([posts_table, users_table])
    assert order.index("users") < order.index("posts")


def test_insertion_order_contains_all_tables(users_table, posts_table):
    order = get_insertion_order([users_table, posts_table])
    assert set(order) == {"users", "posts"}


def test_insertion_order_single_table(users_table):
    order = get_insertion_order([users_table])
    assert order == ["users"]


# ---------------------------------------------------------------------------
# plan_ordered_seed
# ---------------------------------------------------------------------------

def test_plan_ordered_seed_returns_string(users_table):
    result = plan_ordered_seed([users_table], rows_per_table=2)
    assert isinstance(result, str)


def test_plan_ordered_seed_contains_insert(users_table):
    result = plan_ordered_seed([users_table], rows_per_table=1)
    assert "INSERT INTO" in result


def test_plan_ordered_seed_contains_table_comment(users_table):
    result = plan_ordered_seed([users_table], rows_per_table=1)
    assert "-- Table: users" in result


def test_plan_ordered_seed_both_tables_present(users_table, posts_table):
    result = plan_ordered_seed([users_table, posts_table], rows_per_table=1)
    assert "-- Table: users" in result
    assert "-- Table: posts" in result


def test_plan_ordered_seed_users_section_before_posts(users_table, posts_table):
    result = plan_ordered_seed([users_table, posts_table], rows_per_table=1)
    assert result.index("-- Table: users") < result.index("-- Table: posts")


def test_plan_ordered_seed_ends_with_newline(users_table):
    result = plan_ordered_seed([users_table], rows_per_table=1)
    assert result.endswith("\n")


def test_plan_ordered_seed_respects_row_count(users_table):
    result = plan_ordered_seed([users_table], rows_per_table=5)
    insert_count = result.count("INSERT INTO")
    assert insert_count == 5
