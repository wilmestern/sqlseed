"""Tests for sqlseed.row_flattener."""

import pytest

from sqlseed.row_flattener import (
    FlattenerConfig,
    FlattenerError,
    flatten_row,
    flatten_rows,
)


# ---------------------------------------------------------------------------
# FlattenerConfig
# ---------------------------------------------------------------------------

def test_flattener_config_default_separator():
    cfg = FlattenerConfig()
    assert cfg.separator == "."


def test_flattener_config_default_max_depth():
    cfg = FlattenerConfig()
    assert cfg.max_depth == 5


def test_flattener_config_empty_separator_raises():
    with pytest.raises(FlattenerError, match="separator"):
        FlattenerConfig(separator="")


def test_flattener_config_zero_max_depth_raises():
    with pytest.raises(FlattenerError, match="max_depth"):
        FlattenerConfig(max_depth=0)


def test_flattener_config_negative_max_depth_raises():
    with pytest.raises(FlattenerError, match="max_depth"):
        FlattenerConfig(max_depth=-1)


def test_flattener_config_skip_columns_normalised_lowercase():
    cfg = FlattenerConfig(skip_columns=["Meta", "PAYLOAD"])
    assert "meta" in cfg.skip_columns
    assert "payload" in cfg.skip_columns


# ---------------------------------------------------------------------------
# flatten_row — basic behaviour
# ---------------------------------------------------------------------------

def test_flatten_row_scalar_values_unchanged():
    row = {"id": 1, "name": "Alice", "active": True}
    result = flatten_row(row)
    assert result == row


def test_flatten_row_nested_dict_expands():
    row = {"id": 1, "meta": {"city": "London", "zip": "EC1"}}
    result = flatten_row(row)
    assert result["meta.city"] == "London"
    assert result["meta.zip"] == "EC1"
    assert "meta" not in result


def test_flatten_row_deeply_nested():
    row = {"data": {"a": {"b": 42}}}
    result = flatten_row(row)
    assert result["data.a.b"] == 42


def test_flatten_row_custom_separator():
    cfg = FlattenerConfig(separator="__")
    row = {"info": {"score": 99}}
    result = flatten_row(row, cfg)
    assert "info__score" in result


def test_flatten_row_none_value_not_expanded():
    row = {"payload": None}
    result = flatten_row(row)
    assert result["payload"] is None


def test_flatten_row_skip_columns_preserved():
    cfg = FlattenerConfig(skip_columns=["meta"])
    row = {"meta": {"city": "Paris"}, "name": "Bob"}
    result = flatten_row(row, cfg)
    assert "meta" in result
    assert isinstance(result["meta"], dict)


def test_flatten_row_max_depth_limits_expansion():
    cfg = FlattenerConfig(max_depth=1)
    row = {"data": {"nested": {"deep": 1}}}
    result = flatten_row(row, cfg)
    # depth=1 means top-level dict keys get expanded but their children stay as-is
    assert "data.nested" in result
    assert isinstance(result["data.nested"], dict)


# ---------------------------------------------------------------------------
# flatten_rows
# ---------------------------------------------------------------------------

def test_flatten_rows_returns_list():
    rows = [{"a": 1}, {"a": 2}]
    result = flatten_rows(rows)
    assert isinstance(result, list)
    assert len(result) == 2


def test_flatten_rows_empty_input():
    assert flatten_rows([]) == []


def test_flatten_rows_each_row_flattened():
    rows = [
        {"id": 1, "meta": {"tag": "x"}},
        {"id": 2, "meta": {"tag": "y"}},
    ]
    result = flatten_rows(rows)
    assert result[0]["meta.tag"] == "x"
    assert result[1]["meta.tag"] == "y"


def test_flatten_rows_does_not_mutate_originals():
    rows = [{"id": 1, "meta": {"k": "v"}}]
    flatten_rows(rows)
    assert "meta" in rows[0]
