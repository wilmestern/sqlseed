"""Combines row generation with pagination for large-table exports."""

from typing import List, Dict, Any, Iterator

from sqlseed.schema_parser import TableDefinition
from sqlseed.enriched_generator import generate_enriched_row
from sqlseed.row_pagination import PaginationConfig, PageResult, paginate_rows, iter_pages


def generate_all_rows(
    table: TableDefinition,
    count: int,
) -> List[Dict[str, Any]]:
    """Generate *count* enriched rows for *table* in memory."""
    return [generate_enriched_row(table) for _ in range(count)]


def export_page(
    table: TableDefinition,
    count: int,
    config: PaginationConfig,
) -> PageResult:
    """Generate all rows for a table and return a single page."""
    rows = generate_all_rows(table, count)
    return paginate_rows(rows, config)


def export_pages(
    table: TableDefinition,
    count: int,
    page_size: int = 100,
) -> Iterator[PageResult]:
    """Generate all rows for a table and yield successive pages."""
    rows = generate_all_rows(table, count)
    yield from iter_pages(rows, page_size=page_size)


def export_page_as_dicts(
    table: TableDefinition,
    count: int,
    config: PaginationConfig,
) -> Dict[str, Any]:
    """Return a page result serialised as a plain dictionary."""
    result = export_page(table, count, config)
    return {
        "table": table.name,
        "page": result.page,
        "page_size": result.page_size,
        "total": result.total,
        "total_pages": result.total_pages,
        "has_next": result.has_next,
        "has_previous": result.has_previous,
        "rows": result.rows,
    }
