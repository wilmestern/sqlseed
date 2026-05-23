"""Partition rows into named buckets based on column value predicates."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

Row = Dict[str, object]
Predicate = Callable[[Row], bool]


@dataclass
class PartitionConfig:
    """Configuration for row partitioning."""

    default_partition: str = "__other__"

    def __post_init__(self) -> None:
        if not self.default_partition or not self.default_partition.strip():
            raise ValueError("default_partition must be a non-empty string")


@dataclass
class PartitionResult:
    """Holds the bucketed rows after partitioning."""

    buckets: Dict[str, List[Row]] = field(default_factory=dict)

    def get(self, name: str) -> List[Row]:
        """Return rows for *name*, or an empty list if the bucket does not exist."""
        return self.buckets.get(name, [])

    def names(self) -> List[str]:
        """Return sorted bucket names."""
        return sorted(self.buckets.keys())

    def total(self) -> int:
        """Return total number of rows across all buckets."""
        return sum(len(v) for v in self.buckets.values())


def partition_rows(
    rows: List[Row],
    rules: List[tuple[str, Predicate]],
    config: Optional[PartitionConfig] = None,
) -> PartitionResult:
    """Partition *rows* using ordered *rules*.

    Each rule is a ``(name, predicate)`` pair.  The first matching rule wins.
    Rows that match no rule are placed in ``config.default_partition``.
    """
    if config is None:
        config = PartitionConfig()

    result: Dict[str, List[Row]] = {}

    for row in rows:
        placed = False
        for name, predicate in rules:
            if predicate(row):
                result.setdefault(name, []).append(row)
                placed = True
                break
        if not placed:
            result.setdefault(config.default_partition, []).append(row)

    return PartitionResult(buckets=result)


def partition_sizes(result: PartitionResult) -> Dict[str, int]:
    """Return a mapping of bucket name to row count."""
    return {name: len(rows) for name, rows in result.buckets.items()}
