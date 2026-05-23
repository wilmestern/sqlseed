"""Row quality scorer that rates generated rows based on configurable criteria."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from sqlseed.schema_parser import TableDefinition


@dataclass
class ScoringRule:
    name: str
    fn: Callable[[Dict[str, Any], TableDefinition], float]
    weight: float = 1.0

    def __post_init__(self) -> None:
        if not callable(self.fn):
            raise TypeError(f"Scoring rule '{self.name}' fn must be callable")
        if self.weight <= 0:
            raise ValueError(f"Weight for rule '{self.name}' must be positive")


@dataclass
class ScoreResult:
    row: Dict[str, Any]
    total: float
    breakdown: Dict[str, float] = field(default_factory=dict)

    def __str__(self) -> str:
        parts = ", ".join(f"{k}={v:.2f}" for k, v in self.breakdown.items())
        return f"ScoreResult(total={self.total:.2f}, [{parts}])"


class RowScorer:
    """Scores rows using a weighted set of named rules."""

    def __init__(self) -> None:
        self._rules: List[ScoringRule] = []

    def add_rule(self, name: str, fn: Callable[[Dict[str, Any], TableDefinition], float], weight: float = 1.0) -> None:
        if any(r.name == name for r in self._rules):
            raise ValueError(f"Rule '{name}' is already registered")
        self._rules.append(ScoringRule(name=name, fn=fn, weight=weight))

    def remove_rule(self, name: str) -> None:
        self._rules = [r for r in self._rules if r.name != name]

    def clear(self) -> None:
        self._rules.clear()

    def rule_names(self) -> List[str]:
        return [r.name for r in self._rules]

    def score(self, row: Dict[str, Any], table: TableDefinition) -> ScoreResult:
        if not self._rules:
            return ScoreResult(row=row, total=0.0, breakdown={})

        total_weight = sum(r.weight for r in self._rules)
        breakdown: Dict[str, float] = {}
        weighted_sum = 0.0

        for rule in self._rules:
            raw = float(rule.fn(row, table))
            clamped = max(0.0, min(1.0, raw))
            breakdown[rule.name] = clamped
            weighted_sum += clamped * rule.weight

        total = weighted_sum / total_weight
        return ScoreResult(row=row, total=total, breakdown=breakdown)

    def score_rows(self, rows: List[Dict[str, Any]], table: TableDefinition) -> List[ScoreResult]:
        return [self.score(row, table) for row in rows]

    def filter_by_score(self, rows: List[Dict[str, Any]], table: TableDefinition, threshold: float) -> List[Dict[str, Any]]:
        return [r.row for r in self.score_rows(rows, table) if r.total >= threshold]
