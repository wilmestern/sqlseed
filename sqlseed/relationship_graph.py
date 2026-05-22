"""Builds and queries a directed graph of table relationships based on foreign keys."""

from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set

from sqlseed.schema_parser import TableDefinition
from sqlseed.foreign_key_resolver import ForeignKeyConstraint, parse_foreign_keys


@dataclass
class RelationshipGraph:
    """Directed graph where edges represent FK dependencies (from_table -> to_table)."""

    # adjacency: table -> list of tables it depends on
    dependencies: Dict[str, List[str]] = field(default_factory=lambda: defaultdict(list))
    # reverse: table -> list of tables that depend on it
    dependents: Dict[str, List[str]] = field(default_factory=lambda: defaultdict(list))
    tables: Set[str] = field(default_factory=set)


def build_relationship_graph(tables: List[TableDefinition]) -> RelationshipGraph:
    """Construct a RelationshipGraph from a list of TableDefinitions."""
    graph = RelationshipGraph()

    for table in tables:
        graph.tables.add(table.name)

    for table in tables:
        fk_constraints: List[ForeignKeyConstraint] = parse_foreign_keys(table)
        for fk in fk_constraints:
            ref = fk.referenced_table
            graph.dependencies[table.name].append(ref)
            graph.dependents[ref].append(table.name)

    return graph


def topological_sort(graph: RelationshipGraph) -> List[str]:
    """Return tables in insertion order (dependencies first) using Kahn's algorithm."""
    in_degree: Dict[str, int] = {t: 0 for t in graph.tables}
    for table in graph.tables:
        for dep in graph.dependencies.get(table, []):
            if dep in graph.tables:
                in_degree[table] += 1

    queue: deque = deque(sorted(t for t, d in in_degree.items() if d == 0))
    order: List[str] = []

    while queue:
        node = queue.popleft()
        order.append(node)
        for dependent in sorted(graph.dependents.get(node, [])):
            in_degree[dependent] -= 1
            if in_degree[dependent] == 0:
                queue.append(dependent)

    if len(order) != len(graph.tables):
        remaining = graph.tables - set(order)
        raise ValueError(f"Circular dependency detected among tables: {remaining}")

    return order


def get_dependencies(graph: RelationshipGraph, table_name: str) -> List[str]:
    """Return direct dependencies of a table."""
    return graph.dependencies.get(table_name, [])


def get_dependents(graph: RelationshipGraph, table_name: str) -> List[str]:
    """Return tables that directly depend on the given table."""
    return graph.dependents.get(table_name, [])


def get_all_dependencies(graph: RelationshipGraph, table_name: str) -> List[str]:
    """Return all transitive dependencies of a table in breadth-first order.

    The result includes direct and indirect dependencies, but excludes the
    starting table itself. Tables are returned in the order they are first
    encountered during traversal.
    """
    visited: Set[str] = set()
    queue: deque = deque(graph.dependencies.get(table_name, []))
    order: List[str] = []

    while queue:
        dep = queue.popleft()
        if dep in visited:
            continue
        visited.add(dep)
        order.append(dep)
        queue.extend(graph.dependencies.get(dep, []))

    return order
