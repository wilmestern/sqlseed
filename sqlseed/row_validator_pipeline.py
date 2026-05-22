"""Pipeline that runs a sequence of validation steps over generated rows."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

from sqlseed.schema_parser import TableDefinition
from sqlseed.constraint_validator import ValidationResult, check_and_register, UniquenessTracker


ValidationStep = Callable[[TableDefinition, Dict], Optional[str]]


@dataclass
class PipelineResult:
    row: Dict
    passed: bool
    errors: List[str] = field(default_factory=list)

    def __bool__(self) -> bool:
        return self.passed


@dataclass
class RowValidatorPipeline:
    """Runs ordered validation steps against a row dict."""

    _steps: List[tuple[str, ValidationStep]] = field(default_factory=list, init=False)

    def add_step(self, name: str, step: ValidationStep) -> None:
        """Register a named validation step."""
        if not callable(step):
            raise TypeError(f"Validation step '{name}' must be callable.")
        self._steps.append((name, step))

    def remove_step(self, name: str) -> None:
        """Remove a step by name; silently ignores unknown names."""
        self._steps = [(n, s) for n, s in self._steps if n != name]

    def step_names(self) -> List[str]:
        return [n for n, _ in self._steps]

    def run(self, table: TableDefinition, row: Dict) -> PipelineResult:
        """Execute all steps in order, collecting errors."""
        errors: List[str] = []
        for name, step in self._steps:
            error = step(table, row)
            if error:
                errors.append(f"[{name}] {error}")
        return PipelineResult(row=row, passed=len(errors) == 0, errors=errors)


def build_default_pipeline(tracker: Optional[UniquenessTracker] = None) -> RowValidatorPipeline:
    """Return a pipeline with standard constraint validation steps."""
    pipeline = RowValidatorPipeline()

    def nullable_check(table: TableDefinition, row: Dict) -> Optional[str]:
        for col in table.columns:
            if not col.nullable and not col.primary_key and row.get(col.name) is None:
                return f"Column '{col.name}' is NOT NULL but received None."
        return None

    def type_check(table: TableDefinition, row: Dict) -> Optional[str]:
        for col in table.columns:
            value = row.get(col.name)
            if value is None:
                continue
            if col.col_type.upper() in ("INT", "INTEGER", "BIGINT", "SMALLINT"):
                if not isinstance(value, int):
                    return f"Column '{col.name}' expects int, got {type(value).__name__}."
        return None

    def uniqueness_check(table: TableDefinition, row: Dict) -> Optional[str]:
        if tracker is None:
            return None
        result: ValidationResult = check_and_register(tracker, table, row)
        if not result.valid:
            return "; ".join(result.errors)
        return None

    pipeline.add_step("nullable", nullable_check)
    pipeline.add_step("type", type_check)
    pipeline.add_step("uniqueness", uniqueness_check)
    return pipeline
