"""Generates semantically appropriate values based on column name hints and type affinity."""

import random
import string
import uuid
from typing import Any, Optional

from sqlseed.column_type_affinity import get_affinity, get_semantic_hint
from sqlseed.schema_parser import ColumnDefinition


_FIRST_NAMES = ["Alice", "Bob", "Carol", "David", "Eve", "Frank", "Grace", "Hank"]
_LAST_NAMES = ["Smith", "Jones", "Taylor", "Brown", "Wilson", "Davies", "Evans"]
_CITIES = ["London", "Paris", "Berlin", "Madrid", "Rome", "Amsterdam", "Vienna"]
_COUNTRIES = ["US", "GB", "DE", "FR", "ES", "IT", "NL", "AU", "CA"]
_STATUSES = ["active", "inactive", "pending", "archived"]
_CURRENCIES = ["USD", "EUR", "GBP", "JPY", "CAD", "AUD"]
_DOMAINS = ["example.com", "test.org", "demo.net", "sample.io"]


def _slug(text: str) -> str:
    return text.lower().replace(" ", "-")


def _random_ip() -> str:
    return ".".join(str(random.randint(1, 254)) for _ in range(4))


def _random_price() -> float:
    return round(random.uniform(0.99, 999.99), 2)


_SEMANTIC_GENERATORS: dict[str, Any] = {
    "email": lambda: f"{random.choice(_FIRST_NAMES).lower()}.{random.choice(_LAST_NAMES).lower()}@{random.choice(_DOMAINS)}",
    "phone": lambda: f"+1-{random.randint(200,999)}-{random.randint(100,999)}-{random.randint(1000,9999)}",
    "url": lambda: f"https://www.{random.choice(_DOMAINS)}/page/{random.randint(1, 999)}",
    "name": lambda: f"{random.choice(_FIRST_NAMES)} {random.choice(_LAST_NAMES)}",
    "first_name": lambda: random.choice(_FIRST_NAMES),
    "last_name": lambda: random.choice(_LAST_NAMES),
    "username": lambda: f"{random.choice(_FIRST_NAMES).lower()}{random.randint(10, 99)}",
    "password_hash": lambda: "$2b$12$" + "".join(random.choices(string.ascii_letters + string.digits, k=32)),
    "paragraph": lambda: "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
    "sentence": lambda: f"Sample title {random.randint(1, 9999)}",
    "slug": lambda: _slug(f"sample-post-{random.randint(1, 9999)}"),
    "ip_address": _random_ip,
    "country": lambda: random.choice(_COUNTRIES),
    "city": lambda: random.choice(_CITIES),
    "address": lambda: f"{random.randint(1, 999)} {random.choice(_LAST_NAMES)} Street",
    "zip_code": lambda: f"{random.randint(10000, 99999)}",
    "latitude": lambda: round(random.uniform(-90.0, 90.0), 6),
    "longitude": lambda: round(random.uniform(-180.0, 180.0), 6),
    "currency_code": lambda: random.choice(_CURRENCIES),
    "price": _random_price,
    "status": lambda: random.choice(_STATUSES),
}


def generate_semantic_value(column: ColumnDefinition) -> Optional[Any]:
    """Return a semantically appropriate value for *column*, or None if no hint matches."""
    hint = get_semantic_hint(column.name)
    if hint and hint in _SEMANTIC_GENERATORS:
        return _SEMANTIC_GENERATORS[hint]()

    affinity = get_affinity(column.col_type)
    if affinity == "uuid":
        return str(uuid.uuid4())

    return None
