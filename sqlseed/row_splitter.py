"""Row splitter: splits a list of rows into named subsets based on column value predicates."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

Row = Dict[str, object]
Predicate = Callable[[Row], bool]


class SplitterError(Exception):
    """Raised when a splitter configuration or operation fails."""


@dataclass
class SplitterConfig:
    """Configuration for splitting rows into named buckets."""

    default_bucket: str = "other"
    case_sensitive: bool = False

    def __post_init__(self) -> None:
        if not self.default_bucket or not self.default_bucket.strip():
            raise SplitterError("default_bucket must be a non-empty string")
        self.default_bucket = self.default_bucket.strip()


@dataclass
class SplitResult:
    """Holds the named buckets produced by a split operation."""

    buckets: Dict[str, List[Row]] = field(default_factory=dict)
    default_bucket: str = "other"

    def get(self, name: str) -> List[Row]:
        """Return rows in the named bucket, or an empty list."""
        return self.buckets.get(name, [])

    def names(self) -> List[str]:
        """Return all bucket names that contain at least one row."""
        return [k for k, v in self.buckets.items() if v]

    def total(self) -> int:
        """Return the total number of rows across all buckets."""
        return sum(len(v) for v in self.buckets.values())


def split_rows(
    rows: List[Row],
    rules: List[tuple[str, Predicate]],
    config: Optional[SplitterConfig] = None,
) -> SplitResult:
    """Split *rows* into named buckets using ordered *rules*.

    Each row is placed into the first bucket whose predicate returns True.
    Rows that match no rule land in the default bucket.

    Args:
        rows: The rows to split.
        rules: Ordered list of (bucket_name, predicate) pairs.
        config: Optional splitter configuration.

    Returns:
        A SplitResult containing all populated buckets.
    """
    if config is None:
        config = SplitterConfig()

    result: Dict[str, List[Row]] = {}

    for row in rows:
        placed = False
        for bucket_name, predicate in rules:
            try:
                if predicate(row):
                    result.setdefault(bucket_name, []).append(row)
                    placed = True
                    break
            except Exception as exc:  # noqa: BLE001
                raise SplitterError(
                    f"Predicate for bucket '{bucket_name}' raised an error: {exc}"
                ) from exc
        if not placed:
            result.setdefault(config.default_bucket, []).append(row)

    return SplitResult(buckets=result, default_bucket=config.default_bucket)
