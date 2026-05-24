"""High-level helpers that combine row generation with redaction."""
from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from sqlseed.enriched_generator import generate_enriched_row
from sqlseed.row_redactor import RedactorConfig, redact_rows
from sqlseed.schema_parser import TableDefinition


def generate_redacted_rows(
    table: TableDefinition,
    count: int,
    config: RedactorConfig,
) -> List[Dict[str, Any]]:
    """Generate *count* rows for *table* and apply *config* redaction rules."""
    raw = [generate_enriched_row(table) for _ in range(count)]
    return redact_rows(raw, config)


def export_redacted(
    table: TableDefinition,
    count: int,
    config: RedactorConfig,
    *,
    indent: Optional[int] = 2,
) -> str:
    """Return a JSON string of *count* redacted rows for *table*."""
    rows = generate_redacted_rows(table, count, config)
    return json.dumps(rows, indent=indent, default=str)
