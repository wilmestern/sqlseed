"""Export helpers for partitioned row sets."""

from __future__ import annotations

import json
from typing import Dict, List, Optional

from sqlseed.row_partitioner import PartitionConfig, PartitionResult, partition_rows
from sqlseed.enriched_generator import generate_enriched_row
from sqlseed.schema_parser import TableDefinition

Row = Dict[str, object]
Predicate = object  # Callable[[Row], bool]


def generate_and_partition(
    table: TableDefinition,
    count: int,
    rules: list,
    config: Optional[PartitionConfig] = None,
) -> PartitionResult:
    """Generate *count* rows for *table* and immediately partition them."""
    rows: List[Row] = [generate_enriched_row(table) for _ in range(count)]
    return partition_rows(rows, rules, config)


def export_partition_as_json(
    result: PartitionResult,
    name: str,
    indent: int = 2,
) -> str:
    """Serialise a single bucket from *result* to a JSON string."""
    bucket = result.get(name)
    return json.dumps(bucket, indent=indent, default=str)


def export_all_partitions_as_json(
    result: PartitionResult,
    indent: int = 2,
) -> str:
    """Serialise every bucket in *result* to a single JSON object."""
    payload = {name: result.get(name) for name in result.names()}
    return json.dumps(payload, indent=indent, default=str)


def largest_partition(result: PartitionResult) -> str:
    """Return the name of the bucket with the most rows.

    Raises ``ValueError`` if *result* contains no buckets.
    """
    if not result.buckets:
        raise ValueError("PartitionResult contains no buckets")
    return max(result.buckets, key=lambda k: len(result.buckets[k]))
