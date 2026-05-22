"""Pagination support for generated row sequences."""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class PaginationConfig:
    page_size: int = 100
    page: int = 1

    def __post_init__(self) -> None:
        if self.page_size < 1:
            raise ValueError("page_size must be at least 1")
        if self.page < 1:
            raise ValueError("page must be at least 1")

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


@dataclass
class PageResult:
    rows: List[Dict[str, Any]]
    page: int
    page_size: int
    total: int

    @property
    def total_pages(self) -> int:
        if self.page_size == 0:
            return 0
        return (self.total + self.page_size - 1) // self.page_size

    @property
    def has_next(self) -> bool:
        return self.page < self.total_pages

    @property
    def has_previous(self) -> bool:
        return self.page > 1


def paginate_rows(
    rows: List[Dict[str, Any]],
    config: PaginationConfig,
) -> PageResult:
    """Slice a list of rows according to the pagination config."""
    total = len(rows)
    start = config.offset
    end = start + config.page_size
    page_rows = rows[start:end]
    return PageResult(
        rows=page_rows,
        page=config.page,
        page_size=config.page_size,
        total=total,
    )


def iter_pages(
    rows: List[Dict[str, Any]],
    page_size: int = 100,
):
    """Yield successive PageResult objects covering all rows."""
    if page_size < 1:
        raise ValueError("page_size must be at least 1")
    total = len(rows)
    total_pages = max(1, (total + page_size - 1) // page_size)
    for page in range(1, total_pages + 1):
        config = PaginationConfig(page_size=page_size, page=page)
        yield paginate_rows(rows, config)
