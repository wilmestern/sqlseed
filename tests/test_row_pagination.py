"""Tests for sqlseed.row_pagination."""

import pytest
from sqlseed.row_pagination import (
    PaginationConfig,
    PageResult,
    paginate_rows,
    iter_pages,
)


@pytest.fixture
def rows():
    return [{"id": i, "name": f"user_{i}"} for i in range(1, 26)]  # 25 rows


# --- PaginationConfig ---

def test_pagination_config_defaults():
    cfg = PaginationConfig()
    assert cfg.page_size == 100
    assert cfg.page == 1


def test_pagination_config_offset_first_page():
    cfg = PaginationConfig(page_size=10, page=1)
    assert cfg.offset == 0


def test_pagination_config_offset_second_page():
    cfg = PaginationConfig(page_size=10, page=2)
    assert cfg.offset == 10


def test_pagination_config_invalid_page_size_raises():
    with pytest.raises(ValueError, match="page_size"):
        PaginationConfig(page_size=0)


def test_pagination_config_invalid_page_raises():
    with pytest.raises(ValueError, match="page"):
        PaginationConfig(page=0)


# --- paginate_rows ---

def test_paginate_rows_first_page_length(rows):
    cfg = PaginationConfig(page_size=10, page=1)
    result = paginate_rows(rows, cfg)
    assert len(result.rows) == 10


def test_paginate_rows_last_page_partial(rows):
    cfg = PaginationConfig(page_size=10, page=3)
    result = paginate_rows(rows, cfg)
    assert len(result.rows) == 5


def test_paginate_rows_total_is_full_count(rows):
    cfg = PaginationConfig(page_size=10, page=1)
    result = paginate_rows(rows, cfg)
    assert result.total == 25


def test_paginate_rows_correct_items(rows):
    cfg = PaginationConfig(page_size=5, page=2)
    result = paginate_rows(rows, cfg)
    assert result.rows[0]["id"] == 6
    assert result.rows[-1]["id"] == 10


def test_paginate_rows_beyond_end_returns_empty(rows):
    cfg = PaginationConfig(page_size=10, page=10)
    result = paginate_rows(rows, cfg)
    assert result.rows == []


# --- PageResult properties ---

def test_page_result_total_pages(rows):
    cfg = PaginationConfig(page_size=10, page=1)
    result = paginate_rows(rows, cfg)
    assert result.total_pages == 3


def test_page_result_has_next_true(rows):
    cfg = PaginationConfig(page_size=10, page=1)
    result = paginate_rows(rows, cfg)
    assert result.has_next is True


def test_page_result_has_next_false_on_last_page(rows):
    cfg = PaginationConfig(page_size=10, page=3)
    result = paginate_rows(rows, cfg)
    assert result.has_next is False


def test_page_result_has_previous_false_on_first_page(rows):
    cfg = PaginationConfig(page_size=10, page=1)
    result = paginate_rows(rows, cfg)
    assert result.has_previous is False


def test_page_result_has_previous_true_on_second_page(rows):
    cfg = PaginationConfig(page_size=10, page=2)
    result = paginate_rows(rows, cfg)
    assert result.has_previous is True


# --- iter_pages ---

def test_iter_pages_yields_correct_number_of_pages(rows):
    pages = list(iter_pages(rows, page_size=10))
    assert len(pages) == 3


def test_iter_pages_all_rows_covered(rows):
    all_rows = [r for page in iter_pages(rows, page_size=7) for r in page.rows]
    assert len(all_rows) == 25


def test_iter_pages_invalid_page_size_raises(rows):
    with pytest.raises(ValueError):
        list(iter_pages(rows, page_size=0))


def test_iter_pages_empty_input():
    pages = list(iter_pages([], page_size=10))
    assert len(pages) == 1
    assert pages[0].rows == []
