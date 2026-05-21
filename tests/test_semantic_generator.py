"""Tests for sqlseed.semantic_generator."""

import re
import pytest
from sqlseed.schema_parser import ColumnDefinition
from sqlseed.semantic_generator import generate_semantic_value


def _col(name: str, col_type: str, nullable: bool = True) -> ColumnDefinition:
    return ColumnDefinition(
        name=name,
        col_type=col_type,
        nullable=nullable,
        primary_key=False,
        max_length=None,
        default=None,
    )


def test_email_column_returns_valid_email():
    value = generate_semantic_value(_col("email", "varchar"))
    assert value is not None
    assert "@" in value


def test_phone_column_returns_string():
    value = generate_semantic_value(_col("phone", "varchar"))
    assert isinstance(value, str)
    assert len(value) > 5


def test_url_column_starts_with_https():
    value = generate_semantic_value(_col("url", "text"))
    assert isinstance(value, str)
    assert value.startswith("https://")


def test_first_name_column_returns_non_empty_string():
    value = generate_semantic_value(_col("first_name", "varchar"))
    assert isinstance(value, str)
    assert len(value) > 0


def test_status_column_returns_known_status():
    value = generate_semantic_value(_col("status", "varchar"))
    assert value in ("active", "inactive", "pending", "archived")


def test_latitude_returns_float_in_range():
    value = generate_semantic_value(_col("latitude", "decimal"))
    assert isinstance(value, float)
    assert -90.0 <= value <= 90.0


def test_longitude_returns_float_in_range():
    value = generate_semantic_value(_col("longitude", "decimal"))
    assert isinstance(value, float)
    assert -180.0 <= value <= 180.0


def test_price_returns_positive_float():
    value = generate_semantic_value(_col("price", "decimal"))
    assert isinstance(value, float)
    assert value > 0


def test_uuid_affinity_returns_uuid_string():
    value = generate_semantic_value(_col("record_id", "uuid"))
    assert value is not None
    assert re.match(
        r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
        value,
    )


def test_unknown_column_and_type_returns_none():
    value = generate_semantic_value(_col("foobar_xyz", "varchar"))
    assert value is None


def test_slug_column_contains_no_spaces():
    value = generate_semantic_value(_col("slug", "varchar"))
    assert isinstance(value, str)
    assert " " not in value


def test_ip_address_column_matches_ipv4_pattern():
    value = generate_semantic_value(_col("ip_address", "varchar"))
    assert re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", value)
