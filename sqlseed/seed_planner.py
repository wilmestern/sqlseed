"""Plans the full seed generation process respecting FK ordering and context."""

from typing import Dict, List, Optional

from sqlseed.schema_parser import TableDefinition, parse_create_table
from sqlseed.insert_generator import generate_inserts
from sqlseed.foreign_key_resolver import (
    ForeignKeyConstraint,
    ResolutionContext,
    parse_foreign_keys,
    resolve_table_order,
)
from sqlseed.dialect import Dialect, get_dialect


def build_fk_map(
    tables: List[TableDefinition],
    ddl_map: Dict[str, str],
) -> Dict[str, List[ForeignKeyConstraint]]:
    """Build a mapping of table name -> list of FK constraints."""
    fk_map: Dict[str, List[ForeignKeyConstraint]] = {}
    for table in tables:
        ddl = ddl_map.get(table.name, "")
        constraints = parse_foreign_keys(ddl)
        for c in constraints:
            c.from_table = table.name
        if constraints:
            fk_map[table.name] = constraints
    return fk_map


def plan_seed(
    ddl_statements: List[str],
    row_count: int = 10,
    dialect: Optional[str] = None,
) -> str:
    """Parse DDL statements and generate ordered INSERT statements.

    Args:
        ddl_statements: List of CREATE TABLE SQL strings.
        row_count: Number of rows to generate per table.
        dialect: SQL dialect name (postgres, mysql, sqlite).

    Returns:
        A complete SQL seed script as a string.
    """
    resolved_dialect: Dialect = get_dialect(dialect or "postgres")

    tables: List[TableDefinition] = []
    ddl_map: Dict[str, str] = {}

    for ddl in ddl_statements:
        table = parse_create_table(ddl)
        tables.append(table)
        ddl_map[table.name] = ddl

    fk_map = build_fk_map(tables, ddl_map)
    ordered_names = resolve_table_order(tables, fk_map)

    table_lookup = {t.name: t for t in tables}
    blocks: List[str] = []

    for name in ordered_names:
        table = table_lookup[name]
        block = generate_inserts(table, count=row_count, dialect=resolved_dialect)
        blocks.append(block)

    return "\n\n".join(blocks)
