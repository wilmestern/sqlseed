"""Tests for sqlseed.relationship_graph."""

import pytest

from sqlseed.schema_parser import TableDefinition, ColumnDefinition
from sqlseed.relationship_graph import (
    build_relationship_graph,
    topological_sort,
    get_dependencies,
    get_dependents,
    RelationshipGraph,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def users_table():
    return TableDefinition(
        name="users",
        columns=[
            ColumnDefinition(name="id", col_type="INT", nullable=False, primary_key=True),
            ColumnDefinition(name="email", col_type="VARCHAR", nullable=False),
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
        ],
        foreign_keys=[("user_id", "users", "id")],
    )


@pytest.fixture()
def comments_table():
    return TableDefinition(
        name="comments",
        columns=[
            ColumnDefinition(name="id", col_type="INT", nullable=False, primary_key=True),
            ColumnDefinition(name="post_id", col_type="INT", nullable=False),
        ],
        foreign_keys=[("post_id", "posts", "id")],
    )


# ---------------------------------------------------------------------------
# build_relationship_graph
# ---------------------------------------------------------------------------

def test_build_graph_registers_all_tables(users_table, posts_table):
    graph = build_relationship_graph([users_table, posts_table])
    assert "users" in graph.tables
    assert "posts" in graph.tables


def test_build_graph_records_dependency(users_table, posts_table):
    graph = build_relationship_graph([users_table, posts_table])
    assert "users" in get_dependencies(graph, "posts")


def test_build_graph_records_dependent(users_table, posts_table):
    graph = build_relationship_graph([users_table, posts_table])
    assert "posts" in get_dependents(graph, "users")


def test_build_graph_no_fk_has_no_dependencies(users_table):
    graph = build_relationship_graph([users_table])
    assert get_dependencies(graph, "users") == []


# ---------------------------------------------------------------------------
# topological_sort
# ---------------------------------------------------------------------------

def test_topological_sort_users_before_posts(users_table, posts_table):
    graph = build_relationship_graph([users_table, posts_table])
    order = topological_sort(graph)
    assert order.index("users") < order.index("posts")


def test_topological_sort_chain_order(users_table, posts_table, comments_table):
    graph = build_relationship_graph([comments_table, posts_table, users_table])
    order = topological_sort(graph)
    assert order.index("users") < order.index("posts")
    assert order.index("posts") < order.index("comments")


def test_topological_sort_returns_all_tables(users_table, posts_table, comments_table):
    graph = build_relationship_graph([users_table, posts_table, comments_table])
    order = topological_sort(graph)
    assert set(order) == {"users", "posts", "comments"}


def test_topological_sort_single_table(users_table):
    graph = build_relationship_graph([users_table])
    assert topological_sort(graph) == ["users"]
