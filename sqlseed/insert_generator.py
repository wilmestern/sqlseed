"""Generates SQL INSERT statements from table definitions and generated data."""

from typing import List, Optional
from sqlseed.schema_parser import TableDefinition
from sqlseed.data_generator import generate_value


def _format_value(value) -> str:
    """Format a Python value as a SQL literal."""
    if value is None:
        return "NULL"
    if isinstance(value, bool):
        return "1" if value else "0"
    if isinstance(value, (int, float)):
        return str(value)
    escaped = str(value).replace("'", "''")
    return f"'{escaped}'"


def generate_row(table: TableDefinition) -> dict:
    """Generate a single row of data for the given table definition."""
    return {
        col.name: generate_value(col)
        for col in table.columns
    }


def generate_insert(table: TableDefinition, row: Optional[dict] = None) -> str:
    """Generate a single SQL INSERT statement for the given table."""
    if row is None:
        row = generate_row(table)

    columns = ", ".join(row.keys())
    values = ", ".join(_format_value(v) for v in row.values())
    return f"INSERT INTO {table.name} ({columns}) VALUES ({values});"


def generate_inserts(
    table: TableDefinition,
    count: int = 10,
    rows: Optional[List[dict]] = None
) -> List[str]:
    """Generate multiple SQL INSERT statements for the given table."""
    if rows is not None:
        return [generate_insert(table, row) for row in rows]
    return [generate_insert(table) for _ in range(count)]


def generate_seed_script(
    tables: List[TableDefinition],
    count: int = 10
) -> str:
    """Generate a full seed SQL script for multiple tables."""
    sections = []
    for table in tables:
        header = f"-- Seed data for table: {table.name}"
        statements = generate_inserts(table, count=count)
        sections.append("\n".join([header] + statements))
    return "\n\n".join(sections)
