"""High-level helpers that generate rows and immediately encode them."""
from __future__ import annotations

from typing import Any, Dict, List

from sqlseed.enriched_generator import generate_enriched_row
from sqlseed.row_encoder import EncoderConfig, decode_row, encode_row, encode_rows
from sqlseed.schema_parser import TableDefinition


def generate_encoded_rows(
    table: TableDefinition,
    count: int = 10,
    config: EncoderConfig | None = None,
) -> List[str]:
    """Generate *count* rows for *table* and return them as encoded strings."""
    cfg = config or EncoderConfig()
    rows: List[str] = []
    for _ in range(count):
        row = generate_enriched_row(table)
        rows.append(encode_row(row, cfg))
    return rows


def export_encoded(
    table: TableDefinition,
    count: int = 10,
    config: EncoderConfig | None = None,
) -> Dict[str, Any]:
    """Return a dict with metadata and encoded rows ready for transport."""
    cfg = config or EncoderConfig()
    encoded = generate_encoded_rows(table, count=count, config=cfg)
    return {
        "table": table.name,
        "encoding": cfg.encoding,
        "count": len(encoded),
        "rows": encoded,
    }


def roundtrip_rows(
    table: TableDefinition,
    count: int = 5,
    config: EncoderConfig | None = None,
) -> List[Dict[str, Any]]:
    """Generate rows, encode them, then decode — useful for integration tests."""
    cfg = config or EncoderConfig()
    encoded = generate_encoded_rows(table, count=count, config=cfg)
    return [decode_row(e, cfg) for e in encoded]
