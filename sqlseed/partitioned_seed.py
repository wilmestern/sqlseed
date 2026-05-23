"""High-level API: generate, validate, and partition rows in one step."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Callable

from sqlseed.schema_parser import TableDefinition
from sqlseed.validated_seed import generate_valid_rows
from sqlseed.row_partitioner import PartitionConfig, PartitionResult, partition_rows

Row = Dict[str, object]
Predicate = Callable[[Row], bool]
Rules = List[Tuple[str, Predicate]]


class PartitionedSeedError(RuntimeError):
    """Raised when partitioned seed generation fails."""


@dataclass
class PartitionedSeedConfig:
    """Combined configuration for generation and partitioning."""

    count: int = 10
    max_attempts: int = 100
    partition_config: PartitionConfig = field(default_factory=PartitionConfig)

    def __post_init__(self) -> None:
        if self.count < 1:
            raise ValueError("count must be >= 1")
        if self.max_attempts < self.count:
            raise ValueError("max_attempts must be >= count")


def generate_partitioned_rows(
    table: TableDefinition,
    rules: Rules,
    config: Optional[PartitionedSeedConfig] = None,
) -> PartitionResult:
    """Generate validated rows for *table* and partition them using *rules*.

    Parameters
    ----------
    table:
        The target table definition.
    rules:
        Ordered list of ``(name, predicate)`` pairs passed to
        :func:`~sqlseed.row_partitioner.partition_rows`.
    config:
        Optional combined configuration; defaults are used when omitted.

    Returns
    -------
    PartitionResult
        Bucketed rows ready for export or further processing.
    """
    if config is None:
        config = PartitionedSeedConfig()

    try:
        rows = generate_valid_rows(table, config.count, config.max_attempts)
    except Exception as exc:  # pragma: no cover
        raise PartitionedSeedError(
            f"Failed to generate valid rows for table '{table.name}': {exc}"
        ) from exc

    return partition_rows(rows, rules, config.partition_config)


def partition_summary(result: PartitionResult) -> str:
    """Return a human-readable summary of bucket sizes."""
    lines = [f"Partition summary ({result.total()} total rows):"]
    for name in result.names():
        lines.append(f"  {name}: {len(result.get(name))} rows")
    return "\n".join(lines)
