"""Tests for sqlseed.encoded_export."""
from __future__ import annotations

import json

import pytest

from sqlseed.encoded_export import export_encoded, generate_encoded_rows, roundtrip_rows
from sqlseed.row_encoder import EncoderConfig
from sqlseed.schema_parser import ColumnDefinition, TableDefinition


@pytest.fixture()
def simple_table() -> TableDefinition:
    return TableDefinition(
        name="users",
        columns=[
            ColumnDefinition(
                name="id", data_type="INTEGER", nullable=False, primary_key=True
            ),
            ColumnDefinition(
                name="username", data_type="VARCHAR", nullable=False, max_length=50
            ),
            ColumnDefinition(
                name="email", data_type="VARCHAR", nullable=True, max_length=120
            ),
        ],
    )


# --- generate_encoded_rows ---------------------------------------------------

def test_generate_encoded_rows_returns_list(simple_table):
    result = generate_encoded_rows(simple_table, count=5)
    assert isinstance(result, list)


def test_generate_encoded_rows_correct_count(simple_table):
    result = generate_encoded_rows(simple_table, count=7)
    assert len(result) == 7


def test_generate_encoded_rows_each_element_is_string(simple_table):
    result = generate_encoded_rows(simple_table, count=3)
    for item in result:
        assert isinstance(item, str)


def test_generate_encoded_rows_json_decodable(simple_table):
    cfg = EncoderConfig(encoding="json")
    result = generate_encoded_rows(simple_table, count=3, config=cfg)
    for item in result:
        parsed = json.loads(item)
        assert "id" in parsed
        assert "username" in parsed


def test_generate_encoded_rows_base64_json(simple_table):
    cfg = EncoderConfig(encoding="base64_json")
    result = generate_encoded_rows(simple_table, count=2, config=cfg)
    assert len(result) == 2
    import base64
    for item in result:
        raw = base64.b64decode(item.encode("ascii"))
        parsed = json.loads(raw.decode("utf-8"))
        assert "username" in parsed


# --- export_encoded ----------------------------------------------------------

def test_export_encoded_returns_dict(simple_table):
    result = export_encoded(simple_table, count=4)
    assert isinstance(result, dict)


def test_export_encoded_table_name(simple_table):
    result = export_encoded(simple_table, count=4)
    assert result["table"] == "users"


def test_export_encoded_count_matches(simple_table):
    result = export_encoded(simple_table, count=6)
    assert result["count"] == 6
    assert len(result["rows"]) == 6


def test_export_encoded_encoding_field(simple_table):
    cfg = EncoderConfig(encoding="base64_json")
    result = export_encoded(simple_table, count=2, config=cfg)
    assert result["encoding"] == "base64_json"


# --- roundtrip_rows ----------------------------------------------------------

def test_roundtrip_rows_returns_list_of_dicts(simple_table):
    result = roundtrip_rows(simple_table, count=3)
    assert isinstance(result, list)
    for row in result:
        assert isinstance(row, dict)


def test_roundtrip_rows_correct_count(simple_table):
    result = roundtrip_rows(simple_table, count=5)
    assert len(result) == 5


def test_roundtrip_rows_contains_expected_keys(simple_table):
    result = roundtrip_rows(simple_table, count=2)
    for row in result:
        assert "id" in row
        assert "username" in row
        assert "email" in row


def test_roundtrip_rows_pickle_b64(simple_table):
    cfg = EncoderConfig(encoding="pickle_b64")
    result = roundtrip_rows(simple_table, count=3, config=cfg)
    assert len(result) == 3
    for row in result:
        assert "id" in row
