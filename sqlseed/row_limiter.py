"""Row limiter: cap, skip, and window rows from a generated sequence."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Iterator


@dataclass
class LimiterConfig:
    """Configuration for limiting rows."""

    limit: int | None = None
    offset: int = 0
    window: tuple[int, int] | None = None  # (start_inclusive, end_exclusive)

    def __post_init__(self) -> None:
        if self.limit is not None and self.limit < 0:
            raise ValueError("limit must be a non-negative integer or None")
        if self.offset < 0:
            raise ValueError("offset must be a non-negative integer")
        if self.window is not None:
            start, end = self.window
            if start < 0 or end < 0:
                raise ValueError("window bounds must be non-negative")
            if start >= end:
                raise ValueError("window start must be less than window end")


def limit_rows(
    rows: Iterable[dict],
    config: LimiterConfig,
) -> list[dict]:
    """Apply offset, limit, and window constraints to *rows*.

    Window takes precedence over offset + limit when set.
    """
    row_list = list(rows)

    if config.window is not None:
        start, end = config.window
        return row_list[start:end]

    sliced = row_list[config.offset :]
    if config.limit is not None:
        sliced = sliced[: config.limit]
    return sliced


def iter_limited_rows(
    rows: Iterable[dict],
    config: LimiterConfig,
) -> Iterator[dict]:
    """Lazy iterator variant of :func:`limit_rows`."""
    yield from limit_rows(rows, config)


def apply_limit(
    rows: Iterable[dict],
    *,
    limit: int | None = None,
    offset: int = 0,
) -> list[dict]:
    """Convenience wrapper: apply a simple offset + limit."""
    config = LimiterConfig(limit=limit, offset=offset)
    return limit_rows(rows, config)
