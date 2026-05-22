"""Row aggregator: compute summary statistics over generated row sets."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional


@dataclass
class AggregationResult:
    """Holds the result of a single aggregation applied to a column."""

    column: str
    operation: str
    value: Any

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.operation}({self.column}) = {self.value}"


@dataclass
class AggregationReport:
    """Collection of aggregation results for a row set."""

    results: List[AggregationResult] = field(default_factory=list)

    def get(self, column: str, operation: str) -> Optional[Any]:
        """Return the value for a specific column/operation pair, or None."""
        for r in self.results:
            if r.column == column and r.operation == operation:
                return r.value
        return None

    def as_dict(self) -> Dict[str, Any]:
        """Return all results as a flat dict keyed by 'operation(column)'."""
        return {f"{r.operation}({r.column})": r.value for r in self.results}


# Built-in aggregation functions
_BUILT_IN: Dict[str, Callable[[List[Any]], Any]] = {
    "count": lambda vals: len(vals),
    "min": lambda vals: min(v for v in vals if v is not None) if any(v is not None for v in vals) else None,
    "max": lambda vals: max(v for v in vals if v is not None) if any(v is not None for v in vals) else None,
    "sum": lambda vals: sum(v for v in vals if isinstance(v, (int, float))),
    "avg": lambda vals: (
        sum(v for v in vals if isinstance(v, (int, float))) / len([v for v in vals if isinstance(v, (int, float))])
        if any(isinstance(v, (int, float)) for v in vals)
        else None
    ),
    "null_count": lambda vals: sum(1 for v in vals if v is None),
    "distinct_count": lambda vals: len({v for v in vals if v is not None}),
}


def get_aggregation_fn(operation: str) -> Callable[[List[Any]], Any]:
    """Return a built-in aggregation function by name."""
    key = operation.lower()
    if key not in _BUILT_IN:
        raise ValueError(
            f"Unknown aggregation operation '{operation}'. "
            f"Available: {sorted(_BUILT_IN)}"
        )
    return _BUILT_IN[key]


def aggregate_column(
    rows: List[Dict[str, Any]],
    column: str,
    operation: str,
) -> AggregationResult:
    """Apply a single aggregation to one column across all rows."""
    fn = get_aggregation_fn(operation)
    values = [row.get(column) for row in rows]
    return AggregationResult(column=column, operation=operation, value=fn(values))


def aggregate_rows(
    rows: List[Dict[str, Any]],
    specs: List[Dict[str, str]],
) -> AggregationReport:
    """Compute multiple aggregations over a list of row dicts.

    Each spec is a dict with keys 'column' and 'operation'.
    Returns an AggregationReport containing all results.
    """
    report = AggregationReport()
    for spec in specs:
        column = spec["column"]
        operation = spec["operation"]
        result = aggregate_column(rows, column, operation)
        report.results.append(result)
    return report
