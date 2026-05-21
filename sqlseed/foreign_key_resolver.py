"""Resolves foreign key relationships between tables to generate consistent seed data."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from sqlseed.schema_parser import TableDefinition


@dataclass
class ForeignKeyConstraint:
    """Represents a foreign key relationship between two columns."""
    from_table: str
    from_column: str
    to_table: str
    to_column: str


@dataclass
class ResolutionContext:
    """Holds generated primary key values for FK resolution."""
    generated_ids: Dict[str, List] = field(default_factory=dict)

    def register(self, table: str, column: str, value) -> None:
        key = f"{table}.{column}"
        self.generated_ids.setdefault(key, []).append(value)

    def lookup(self, table: str, column: str) -> Optional[list]:
        key = f"{table}.{column}"
        return self.generated_ids.get(key)


def parse_foreign_keys(sql: str) -> List[ForeignKeyConstraint]:
    """Extract FOREIGN KEY constraints from a CREATE TABLE statement."""
    import re
    constraints = []
    pattern = re.compile(
        r'FOREIGN\s+KEY\s*\(([^)]+)\)\s+REFERENCES\s+(\w+)\s*\(([^)]+)\)',
        re.IGNORECASE
    )
    for match in pattern.finditer(sql):
        from_col = match.group(1).strip().strip('`"[]')
        ref_table = match.group(2).strip()
        ref_col = match.group(3).strip().strip('`"[]')
        constraints.append(ForeignKeyConstraint(
            from_table="",
            from_column=from_col,
            to_table=ref_table,
            to_column=ref_col,
        ))
    return constraints


def resolve_table_order(tables: List[TableDefinition], fk_map: Dict[str, List[ForeignKeyConstraint]]) -> List[str]:
    """Return table names sorted so dependencies come before dependents."""
    table_names = {t.name for t in tables}
    order: List[str] = []
    visited: set = set()

    def visit(name: str) -> None:
        if name in visited:
            return
        visited.add(name)
        for fk in fk_map.get(name, []):
            if fk.to_table in table_names:
                visit(fk.to_table)
        order.append(name)

    for table in tables:
        visit(table.name)

    return order
