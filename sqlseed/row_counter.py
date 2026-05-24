"""Row counting utilities for tracking and reporting row generation statistics."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class CounterError(Exception):
    message: str

    def __str__(self) -> str:
        return self.message


@dataclass
class TableCount:
    table_name: str
    expected: int
    actual: int

    @property
    def is_complete(self) -> bool:
        return self.actual >= self.expected

    @property
    def missing(self) -> int:
        return max(0, self.expected - self.actual)

    def __str__(self) -> str:
        status = "OK" if self.is_complete else f"MISSING {self.missing}"
        return f"{self.table_name}: {self.actual}/{self.expected} [{status}]"


@dataclass
class RowCounter:
    _counts: Dict[str, TableCount] = field(default_factory=dict)

    def register(self, table_name: str, expected: int) -> None:
        if expected < 0:
            raise CounterError(f"Expected count must be non-negative, got {expected}")
        key = table_name.lower()
        self._counts[key] = TableCount(
            table_name=table_name,
            expected=expected,
            actual=0,
        )

    def increment(self, table_name: str, amount: int = 1) -> None:
        key = table_name.lower()
        if key not in self._counts:
            raise CounterError(f"Table '{table_name}' is not registered")
        if amount < 0:
            raise CounterError(f"Increment amount must be non-negative, got {amount}")
        self._counts[key].actual += amount

    def get(self, table_name: str) -> Optional[TableCount]:
        return self._counts.get(table_name.lower())

    def all_complete(self) -> bool:
        return all(tc.is_complete for tc in self._counts.values())

    def incomplete_tables(self) -> List[TableCount]:
        return [tc for tc in self._counts.values() if not tc.is_complete]

    def summary(self) -> Dict[str, dict]:
        return {
            tc.table_name: {
                "expected": tc.expected,
                "actual": tc.actual,
                "complete": tc.is_complete,
                "missing": tc.missing,
            }
            for tc in self._counts.values()
        }

    def reset(self, table_name: str) -> None:
        key = table_name.lower()
        if key in self._counts:
            self._counts[key].actual = 0

    def reset_all(self) -> None:
        for tc in self._counts.values():
            tc.actual = 0
