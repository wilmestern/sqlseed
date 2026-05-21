"""Graph-aware seed planner that uses RelationshipGraph for correct insertion order."""

from __future__ import annotations

from typing import List, Optional

from sqlseed.schema_parser import TableDefinition
from sqlseed.relationship_graph import build_relationship_graph, topological_sort
from sqlseed.insert_generator import generate_inserts
from sqlseed.foreign_key_resolver import ResolutionContext
from sqlseed.validated_seed import generate_valid_rows
from sqlseed.dialect import Dialect, get_dialect


def plan_ordered_seed(
    tables: List[TableDefinition],
    rows_per_table: int = 10,
    dialect: str = "postgres",
    use_validation: bool = True,
) -> str:
    """Generate a complete seed script with tables ordered by FK dependencies.

    Args:
        tables: All table definitions to seed.
        rows_per_table: Number of rows to generate per table.
        dialect: SQL dialect name (postgres, mysql, sqlite).
        use_validation: Whether to use constraint-validated row generation.

    Returns:
        A SQL string with INSERT statements in dependency order.
    """
    graph = build_relationship_graph(tables)
    ordered_names = topological_sort(graph)

    table_map = {t.name: t for t in tables}
    dialect_obj: Dialect = get_dialect(dialect)
    context = ResolutionContext()

    sections: List[str] = []

    for table_name in ordered_names:
        if table_name not in table_map:
            continue
        table = table_map[table_name]

        if use_validation:
            rows = generate_valid_rows(table, count=rows_per_table, context=context)
        else:
            rows = [
                {col.name: None for col in table.columns}
                for _ in range(rows_per_table)
            ]

        sql_block = generate_inserts(
            table=table,
            rows=rows,
            dialect=dialect_obj,
        )
        sections.append(f"-- Table: {table_name}\n{sql_block}")

    return "\n\n".join(sections) + "\n"


def get_insertion_order(tables: List[TableDefinition]) -> List[str]:
    """Return table names in safe insertion order."""
    graph = build_relationship_graph(tables)
    return topological_sort(graph)
