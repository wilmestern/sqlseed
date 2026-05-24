"""Tests for sqlseed.row_encoder."""
from __future__ import annotations

import base64
import json
import pickle

import pytest

from sqlseed.row_encoder import (
    EncoderConfig,
    EncoderError,
    decode_row,
    encode_row,
    encode_rows,
)

ROW: dict = {"id": 1, "name": "Alice", "score": 9.5, "active": True, "note": None}


# --- EncoderConfig -----------------------------------------------------------

def test_encoder_config_defaults():
    cfg = EncoderConfig()
    assert cfg.encoding == "json"
    assert cfg.indent is None
    assert cfg.ensure_ascii is True


def test_encoder_config_invalid_encoding_raises():
    with pytest.raises(EncoderError, match="Unsupported encoding"):
        EncoderConfig(encoding="xml")  # type: ignore[arg-type]


def test_encoder_config_negative_indent_raises():
    with pytest.raises(EncoderError, match="indent"):
        EncoderConfig(indent=-1)


def test_encoder_config_zero_indent_is_valid():
    cfg = EncoderConfig(indent=0)
    assert cfg.indent == 0


# --- encode_row / decode_row (json) ------------------------------------------

def test_encode_row_json_returns_string():
    result = encode_row(ROW)
    assert isinstance(result, str)


def test_encode_row_json_is_valid_json():
    result = encode_row(ROW)
    parsed = json.loads(result)
    assert parsed["id"] == 1
    assert parsed["name"] == "Alice"


def test_encode_row_json_none_preserved():
    result = encode_row(ROW)
    parsed = json.loads(result)
    assert parsed["note"] is None


def test_decode_row_json_roundtrip():
    encoded = encode_row(ROW)
    decoded = decode_row(encoded)
    assert decoded["id"] == ROW["id"]
    assert decoded["name"] == ROW["name"]


# --- encode_row (base64_json) -------------------------------------------------

def test_encode_row_base64_json_returns_string():
    cfg = EncoderConfig(encoding="base64_json")
    result = encode_row(ROW, cfg)
    assert isinstance(result, str)


def test_encode_row_base64_json_is_valid_base64():
    cfg = EncoderConfig(encoding="base64_json")
    result = encode_row(ROW, cfg)
    decoded_bytes = base64.b64decode(result.encode("ascii"))
    parsed = json.loads(decoded_bytes.decode("utf-8"))
    assert parsed["name"] == "Alice"


def test_decode_row_base64_json_roundtrip():
    cfg = EncoderConfig(encoding="base64_json")
    encoded = encode_row(ROW, cfg)
    decoded = decode_row(encoded, cfg)
    assert decoded["score"] == ROW["score"]


# --- encode_row (pickle_b64) --------------------------------------------------

def test_encode_row_pickle_b64_returns_string():
    cfg = EncoderConfig(encoding="pickle_b64")
    result = encode_row(ROW, cfg)
    assert isinstance(result, str)


def test_decode_row_pickle_b64_roundtrip():
    cfg = EncoderConfig(encoding="pickle_b64")
    encoded = encode_row(ROW, cfg)
    decoded = decode_row(encoded, cfg)
    assert decoded["active"] == ROW["active"]


# --- encode_rows -------------------------------------------------------------

def test_encode_rows_returns_list():
    rows = [ROW, {"id": 2, "name": "Bob", "score": 7.0, "active": False, "note": "hi"}]
    result = encode_rows(rows)
    assert isinstance(result, list)
    assert len(result) == 2


def test_encode_rows_each_element_decodable():
    rows = [ROW, {"id": 2, "name": "Bob", "score": 7.0, "active": False, "note": "hi"}]
    encoded = encode_rows(rows)
    for enc, original in zip(encoded, rows):
        decoded = decode_row(enc)
        assert decoded["id"] == original["id"]
