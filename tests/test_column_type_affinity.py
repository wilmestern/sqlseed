"""Tests for sqlseed.column_type_affinity."""

import pytest
from sqlseed.column_type_affinity import get_affinity, get_semantic_hint


@pytest.mark.parametrize("sql_type,expected", [
    ("int", "integer"),
    ("INTEGER", "integer"),
    ("bigint", "integer"),
    ("varchar", "text"),
    ("VARCHAR(255)", "text"),
    ("text", "text"),
    ("boolean", "boolean"),
    ("bool", "boolean"),
    ("date", "date"),
    ("timestamp", "datetime"),
    ("TIMESTAMPTZ", "datetime"),
    ("numeric", "decimal"),
    ("float", "decimal"),
    ("json", "json"),
    ("jsonb", "json"),
    ("uuid", "uuid"),
    ("bytea", "binary"),
    ("blob", "binary"),
])
def test_get_affinity_known_types(sql_type, expected):
    assert get_affinity(sql_type) == expected


def test_get_affinity_unknown_type_returns_text():
    assert get_affinity("geometry") == "text"


def test_get_affinity_strips_length_parameter():
    assert get_affinity("character varying(100)") == "text"


def test_get_affinity_case_insensitive():
    assert get_affinity("BOOLEAN") == "boolean"


@pytest.mark.parametrize("col_name,expected_hint", [
    ("email", "email"),
    ("phone", "phone"),
    ("url", "url"),
    ("first_name", "first_name"),
    ("last_name", "last_name"),
    ("username", "username"),
    ("description", "paragraph"),
    ("bio", "paragraph"),
    ("title", "sentence"),
    ("slug", "slug"),
    ("ip_address", "ip_address"),
    ("country", "country"),
    ("city", "city"),
    ("address", "address"),
    ("zip", "zip_code"),
    ("postal_code", "zip_code"),
    ("latitude", "latitude"),
    ("longitude", "longitude"),
    ("currency", "currency_code"),
    ("price", "price"),
    ("amount", "price"),
    ("status", "status"),
])
def test_get_semantic_hint_known_columns(col_name, expected_hint):
    assert get_semantic_hint(col_name) == expected_hint


def test_get_semantic_hint_unknown_column_returns_none():
    assert get_semantic_hint("foobar_xyz") is None


def test_get_semantic_hint_case_insensitive():
    assert get_semantic_hint("EMAIL") == "email"
    assert get_semantic_hint("Status") == "status"
