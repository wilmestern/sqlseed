"""Maps SQL column types to semantic affinity groups for smarter data generation."""

from dataclasses import dataclass
from typing import Optional


AFFINITY_MAP: dict[str, str] = {
    # Numeric
    "int": "integer",
    "integer": "integer",
    "bigint": "integer",
    "smallint": "integer",
    "tinyint": "integer",
    "serial": "integer",
    "bigserial": "integer",
    "numeric": "decimal",
    "decimal": "decimal",
    "float": "decimal",
    "real": "decimal",
    "double precision": "decimal",
    # Text
    "varchar": "text",
    "character varying": "text",
    "char": "text",
    "text": "text",
    "nvarchar": "text",
    "nchar": "text",
    # Boolean
    "boolean": "boolean",
    "bool": "boolean",
    # Date / time
    "date": "date",
    "time": "time",
    "datetime": "datetime",
    "timestamp": "datetime",
    "timestamptz": "datetime",
    # Binary / blob
    "blob": "binary",
    "bytea": "binary",
    "binary": "binary",
    "varbinary": "binary",
    # JSON
    "json": "json",
    "jsonb": "json",
    # UUID
    "uuid": "uuid",
}

SEMANTIC_HINTS: dict[str, str] = {
    "email": "email",
    "phone": "phone",
    "url": "url",
    "name": "name",
    "first_name": "first_name",
    "last_name": "last_name",
    "username": "username",
    "password": "password_hash",
    "description": "paragraph",
    "bio": "paragraph",
    "title": "sentence",
    "slug": "slug",
    "ip": "ip_address",
    "ip_address": "ip_address",
    "country": "country",
    "city": "city",
    "address": "address",
    "zip": "zip_code",
    "postal_code": "zip_code",
    "latitude": "latitude",
    "longitude": "longitude",
    "currency": "currency_code",
    "price": "price",
    "amount": "price",
    "status": "status",
}


def get_affinity(sql_type: str) -> str:
    """Return the affinity group for a SQL type string."""
    normalized = sql_type.lower().split("(")[0].strip()
    return AFFINITY_MAP.get(normalized, "text")


def get_semantic_hint(column_name: str) -> Optional[str]:
    """Return a semantic hint for a column name if one is recognised."""
    key = column_name.lower()
    return SEMANTIC_HINTS.get(key)
