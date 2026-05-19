"""SQL dialect support for insert statement formatting."""

from enum import Enum
from typing import Optional


class Dialect(str, Enum):
    MYSQL = "mysql"
    POSTGRES = "postgres"
    SQLITE = "sqlite"


DEFAULT_DIALECT = Dialect.POSTGRES


def get_dialect(name: str) -> Dialect:
    """Return a Dialect enum from a string name, case-insensitive."""
    try:
        return Dialect(name.lower())
    except ValueError:
        supported = ", ".join(d.value for d in Dialect)
        raise ValueError(f"Unsupported dialect '{name}'. Supported: {supported}")


def format_identifier(name: str, dialect: Dialect) -> str:
    """Quote an identifier (table or column name) according to dialect."""
    if dialect == Dialect.MYSQL:
        return f"`{name}`"
    elif dialect == Dialect.POSTGRES:
        return f'"{name}"'
    elif dialect == Dialect.SQLITE:
        return f'"{name}"'
    return name


def format_placeholder(index: int, dialect: Dialect) -> str:
    """Return a value placeholder (used in parameterized queries)."""
    if dialect == Dialect.MYSQL:
        return "%s"
    elif dialect == Dialect.POSTGRES:
        return f"${index}"
    elif dialect == Dialect.SQLITE:
        return "?"
    return "%s"


def build_insert_statement(
    table_name: str,
    columns: list[str],
    values: list[str],
    dialect: Dialect,
    use_placeholders: bool = False,
) -> str:
    """Build a full INSERT statement string for the given dialect."""
    quoted_table = format_identifier(table_name, dialect)
    quoted_columns = ", ".join(format_identifier(col, dialect) for col in columns)

    if use_placeholders:
        value_list = ", ".join(
            format_placeholder(i + 1, dialect) for i in range(len(values))
        )
    else:
        value_list = ", ".join(values)

    return f"INSERT INTO {quoted_table} ({quoted_columns}) VALUES ({value_list});"
