"""Parse SQL CREATE TABLE statements into structured schema definitions."""

import re
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ColumnDefinition:
    name: str
    data_type: str
    nullable: bool = True
    primary_key: bool = False
    unique: bool = False
    default: Optional[str] = None
    max_length: Optional[int] = None


@dataclass
class TableDefinition:
    name: str
    columns: list[ColumnDefinition] = field(default_factory=list)


COLUMN_PATTERN = re.compile(
    r'^\s*`?(?P<name>\w+)`?\s+'
    r'(?P<type>[A-Z]+)(?:\((?P<length>\d+)\))?'
    r'(?P<attrs>.*)$',
    re.IGNORECASE,
)

TABLE_PATTERN = re.compile(
    r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?`?(?P<name>\w+)`?\s*\(',
    re.IGNORECASE,
)


def parse_column(line: str) -> Optional[ColumnDefinition]:
    """Parse a single column definition line."""
    line = line.strip().rstrip(',')
    skip_prefixes = ('primary key', 'unique', 'index', 'key', 'constraint', ')')
    if any(line.lower().startswith(p) for p in skip_prefixes):
        return None

    match = COLUMN_PATTERN.match(line)
    if not match:
        return None

    name = match.group('name')
    data_type = match.group('type').upper()
    length_str = match.group('length')
    attrs = match.group('attrs').upper()

    return ColumnDefinition(
        name=name,
        data_type=data_type,
        nullable='NOT NULL' not in attrs,
        primary_key='PRIMARY KEY' in attrs,
        unique='UNIQUE' in attrs,
        max_length=int(length_str) if length_str else None,
    )


def parse_create_table(sql: str) -> Optional[TableDefinition]:
    """Parse a CREATE TABLE SQL statement into a TableDefinition."""
    table_match = TABLE_PATTERN.search(sql)
    if not table_match:
        return None

    table = TableDefinition(name=table_match.group('name'))

    body_start = sql.index('(', table_match.start()) + 1
    depth = 1
    body_end = body_start
    while body_end < len(sql) and depth > 0:
        if sql[body_end] == '(':
            depth += 1
        elif sql[body_end] == ')':
            depth -= 1
        body_end += 1

    body = sql[body_start:body_end - 1]
    for line in body.splitlines():
        col = parse_column(line)
        if col:
            table.columns.append(col)

    return table
