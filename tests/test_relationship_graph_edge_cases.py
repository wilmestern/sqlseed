"""Edge-case tests for relationship_graph: isolated tables, multi-FK, etc."""

import pytest

from sqlseed.schema_parser import TableDefinition, ColumnDefinition
from sqlseed.relationship_graph import (
    build_relationship_graph,
    topological_sort,
    get_dependencies,
    get_dependents,
)


def _make_table(name: str, fk_list=None) -> TableDefinition:
    return TableDefinition(
        name=name,
        columns=[
            ColumnDefinition(name="id", col_type="INT", nullable=False, primary_key=True),
        ],
        foreign_keys=fk_list or [],
    )


def test_empty_table_list_produces_empty_graph():
    graph = build_relationship_graph([])
    assert len(graph.tables) == 0
    assert topological_sort(graph) == []


def test_multiple_isolated_tables_all_present():
    tables = [_make_table("a"), _make_table("b"), _make_table("c")]
    graph = build_relationship_graph(tables)
    order = topological_sort(graph)
    assert set(order) == {"a", "b", "c"}


def test_multiple_isolated_tables_no_dependencies():
    tables = [_make_table("x"), _make_table("y")]
    graph = build_relationship_graph(tables)
    assert get_dependencies(graph, "x") == []
    assert get_dependencies(graph, "y") == []


def test_table_with_two_foreign_keys():
    """A table referencing two others should depend on both."""
    a = _make_table("a")
    b = _make_table("b")
    c = TableDefinition(
        name="c",
        columns=[
            ColumnDefinition(name="id", col_type="INT", nullable=False, primary_key=True),
            ColumnDefinition(name="a_id", col_type="INT", nullable=True),
            ColumnDefinition(name="b_id", col_type="INT", nullable=True),
        ],
        foreign_keys=[("a_id", "a", "id"), ("b_id", "b", "id")],
    )
    graph = build_relationship_graph([a, b, c])
    deps = get_dependencies(graph, "c")
    assert "a" in deps
    assert "b" in deps


def test_topological_sort_two_fk_deps_before_child():
    a = _make_table("a")
    b = _make_table("b")
    c = TableDefinition(
        name="c",
        columns=[
            ColumnDefinition(name="id", col_type="INT", nullable=False, primary_key=True),
            ColumnDefinition(name="a_id", col_type="INT", nullable=True),
            ColumnDefinition(name="b_id", col_type="INT", nullable=True),
        ],
        foreign_keys=[("a_id", "a", "id"), ("b_id", "b", "id")],
    )
    graph = build_relationship_graph([a, b, c])
    order = topological_sort(graph)
    assert order.index("a") < order.index("c")
    assert order.index("b") < order.index("c")


def test_get_dependents_unknown_table_returns_empty():
    graph = build_relationship_graph([_make_table("z")])
    assert get_dependents(graph, "nonexistent") == []


def test_get_dependencies_unknown_table_returns_empty():
    graph = build_relationship_graph([_make_table("z")])
    assert get_dependencies(graph, "nonexistent") == []
