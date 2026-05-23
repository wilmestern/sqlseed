"""row_caster.py — Cast row values to target Python types based on column affinity."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from sqlseed.schema_parser import TableDefinition
from sqlseed.column_type_affinity import get_affinity


class CastError(ValueError):
    """Raised when a value cannot be cast to the required type."""


# Default casters keyed by affinity string
_DEFAULT_CASTERS: Dict[str, Callable[[Any], Any]] = {
    "integer": int,
    "real": float,
    "text": str,
    "boolean": bool,
    "date": str,
    "datetime": str,
    "blob": bytes,
}


@dataclass
class CasterConfig:
    """Configuration for the row caster."""

    strict: bool = False
    """If True, raise CastError on failure; otherwise leave value unchanged."""

    custom: Dict[str, Callable[[Any], Any]] = field(default_factory=dict)
    """Column-level overrides: {column_name_lower: callable}."""

    def __post_init__(self) -> None:
        self.custom = {k.lower(): v for k, v in self.custom.items()}


def _cast_value(
    value: Any,
    affinity: str,
    strict: bool,
    casters: Dict[str, Callable[[Any], Any]],
) -> Any:
    if value is None:
        return None
    caster = casters.get(affinity)
    if caster is None:
        return value
    try:
        return caster(value)
    except (ValueError, TypeError) as exc:
        if strict:
            raise CastError(
                f"Cannot cast {value!r} to affinity '{affinity}': {exc}"
            ) from exc
        return value


def cast_row(
    row: Dict[str, Any],
    table: TableDefinition,
    config: Optional[CasterConfig] = None,
) -> Dict[str, Any]:
    """Return a new row with values cast according to column affinities."""
    if config is None:
        config = CasterConfig()

    effective_casters = {**_DEFAULT_CASTERS}
    result: Dict[str, Any] = {}

    for col in table.columns:
        col_lower = col.name.lower()
        value = row.get(col.name)

        if col_lower in config.custom:
            caster = config.custom[col_lower]
            try:
                result[col.name] = caster(value) if value is not None else None
            except (ValueError, TypeError) as exc:
                if config.strict:
                    raise CastError(
                        f"Custom cast failed for '{col.name}': {exc}"
                    ) from exc
                result[col.name] = value
        else:
            affinity = get_affinity(col.col_type)
            result[col.name] = _cast_value(
                value, affinity, config.strict, effective_casters
            )

    return result


def cast_rows(
    rows: List[Dict[str, Any]],
    table: TableDefinition,
    config: Optional[CasterConfig] = None,
) -> List[Dict[str, Any]]:
    """Cast every row in *rows* and return a new list."""
    return [cast_row(row, table, config) for row in rows]
