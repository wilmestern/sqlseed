"""Generate realistic fake data based on column definitions."""

import random
import string
import uuid
from datetime import date, datetime, timedelta
from typing import Any

from sqlseed.schema_parser import ColumnDefinition


def _random_string(max_length: int = 32) -> str:
    length = random.randint(4, min(max_length, 32))
    return ''.join(random.choices(string.ascii_lowercase, k=length))


def _random_email() -> str:
    user = _random_string(8)
    domain = _random_string(6)
    return f"{user}@{domain}.com"


def _random_date() -> str:
    start = date(2000, 1, 1)
    offset = random.randint(0, 365 * 24)
    return (start + timedelta(days=offset)).isoformat()


def _random_datetime() -> str:
    start = datetime(2000, 1, 1)
    offset = random.randint(0, 365 * 24 * 3600)
    return (start + timedelta(seconds=offset)).strftime('%Y-%m-%d %H:%M:%S')


NAME_HINTS = ('name', 'title', 'label', 'slug')
EMAIL_HINTS = ('email', 'mail')
DESC_HINTS = ('description', 'body', 'content', 'note', 'comment', 'text')


def generate_value(col: ColumnDefinition) -> Any:
    """Generate a single fake value appropriate for the given column."""
    if not col.nullable and col.default is None and col.data_type in ('INT', 'INTEGER', 'BIGINT', 'SMALLINT'):
        if col.primary_key:
            return None  # caller should handle auto-increment

    dtype = col.data_type
    col_lower = col.name.lower()

    if dtype in ('INT', 'INTEGER', 'BIGINT', 'SMALLINT', 'TINYINT'):
        return random.randint(1, 10_000)

    if dtype in ('FLOAT', 'DOUBLE', 'DECIMAL', 'NUMERIC', 'REAL'):
        return round(random.uniform(0.01, 9999.99), 2)

    if dtype == 'BOOLEAN':
        return random.choice([True, False])

    if dtype == 'DATE':
        return _random_date()

    if dtype in ('DATETIME', 'TIMESTAMP'):
        return _random_datetime()

    if dtype in ('UUID',):
        return str(uuid.uuid4())

    if dtype in ('TEXT', 'MEDIUMTEXT', 'LONGTEXT', 'CLOB'):
        if any(h in col_lower for h in DESC_HINTS):
            return ' '.join(_random_string(8) for _ in range(random.randint(5, 15)))
        return _random_string(64)

    # VARCHAR, CHAR, and others
    max_len = col.max_length or 255
    if any(h in col_lower for h in EMAIL_HINTS):
        return _random_email()[:max_len]
    if any(h in col_lower for h in NAME_HINTS):
        return _random_string(min(max_len, 20)).capitalize()

    return _random_string(min(max_len, 32))
