"""Export utilities that operate on grouped row sets."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from sqlseed.row_grouper import GrouperConfig, group_rows, group_sizes, largest_group
from sqlseed.row_serializer import serialize_rows
from sqlseed.schema_parser import TableDefinition


def export_groups_as_dict(
    rows: List[Dict[str, Any]],
    config: GrouperConfig,
    table: Optional[TableDefinition] = None,
) -> Dict[str, Any]:
    """Group *rows* and return a summary dict with group data and sizes."""
    groups = group_rows(rows, config)
    sizes = group_sizes(groups)
    return {
        "key_columns": config.key_columns,
        "group_count": len(groups),
        "sizes": {str(k): v for k, v in sizes.items()},
        "groups": {
            str(k): v for k, v in groups.items()
        },
    }


def export_group_as_json(
    rows: List[Dict[str, Any]],
    config: GrouperConfig,
    key: Tuple[Any, ...],
    table: Optional[TableDefinition] = None,
    fmt: str = "json",
) -> str:
    """Serialise the rows belonging to a single group *key*."""
    groups = group_rows(rows, config)
    group_rows_list = groups.get(key, [])
    if table is not None:
        return serialize_rows(group_rows_list, table, fmt=fmt)
    import json
    return json.dumps(group_rows_list, default=str, indent=2)


def export_largest_group(
    rows: List[Dict[str, Any]],
    config: GrouperConfig,
    table: Optional[TableDefinition] = None,
    fmt: str = "json",
) -> str:
    """Serialise the rows from the largest group."""
    groups = group_rows(rows, config)
    result = largest_group(groups)
    if result is None:
        return "[]"
    _, group_rows_list = result
    if table is not None:
        return serialize_rows(group_rows_list, table, fmt=fmt)
    import json
    return json.dumps(group_rows_list, default=str, indent=2)
