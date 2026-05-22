"""batch_exporter.py — Export multiple tables' seed data in a single pass."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from sqlseed.schema_parser import TableDefinition
from sqlseed.insert_generator import generate_inserts
from sqlseed.graph_seed_planner import get_insertion_order
from sqlseed.output_writer import build_output


@dataclass
class BatchExportConfig:
    """Configuration for a batch export run."""

    tables: List[TableDefinition]
    row_counts: Dict[str, int] = field(default_factory=dict)
    default_count: int = 10
    dialect: str = "postgres"
    include_header: bool = True
    separator: str = "\n-- ---\n"

    def count_for(self, table_name: str) -> int:
        """Return the row count for *table_name*, falling back to *default_count*."""
        return self.row_counts.get(table_name, self.default_count)


def export_tables(
    config: BatchExportConfig,
    ordered: Optional[List[TableDefinition]] = None,
) -> str:
    """Generate seed SQL for all tables in dependency order.

    Parameters
    ----------
    config:
        Export configuration including tables, row counts, and dialect.
    ordered:
        Pre-computed insertion order.  When *None* the order is derived
        automatically via :func:`get_insertion_order`.

    Returns
    -------
    str
        A single SQL string containing INSERT statements for every table.
    """
    if ordered is None:
        ordered = get_insertion_order(config.tables)

    sections: List[str] = []
    for table in ordered:
        count = config.count_for(table.name)
        sql_block = generate_inserts(
            table,
            count=count,
            dialect=config.dialect,
        )
        sections.append(sql_block)

    combined_sql = config.separator.join(sections)
    return build_output(
        combined_sql,
        include_header=config.include_header,
        source_label="batch export",
    )


def export_table_map(
    config: BatchExportConfig,
) -> Dict[str, str]:
    """Return a mapping of table name → individual INSERT SQL block.

    Useful when callers want to write one file per table.
    """
    ordered = get_insertion_order(config.tables)
    result: Dict[str, str] = {}
    for table in ordered:
        count = config.count_for(table.name)
        result[table.name] = generate_inserts(
            table,
            count=count,
            dialect=config.dialect,
        )
    return result
