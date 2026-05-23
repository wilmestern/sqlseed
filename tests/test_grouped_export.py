"""Tests for sqlseed.grouped_export."""

import json

import pytest

from sqlseed.grouped_export import (
    export_group_as_json,
    export_groups_as_dict,
    export_largest_group,
)
from sqlseed.row_grouper import GrouperConfig


@pytest.fixture()
def rows():
    return [
        {"id": 1, "role": "admin", "name": "Alice"},
        {"id": 2, "role": "user", "name": "Bob"},
        {"id": 3, "role": "admin", "name": "Carol"},
        {"id": 4, "role": "user", "name": "Dave"},
        {"id": 5, "role": "user", "name": "Eve"},
    ]


def test_export_groups_as_dict_group_count(rows):
    cfg = GrouperConfig(key_columns=["role"])
    result = export_groups_as_dict(rows, cfg)
    assert result["group_count"] == 2


def test_export_groups_as_dict_key_columns(rows):
    cfg = GrouperConfig(key_columns=["role"])
    result = export_groups_as_dict(rows, cfg)
    assert result["key_columns"] == ["role"]


def test_export_groups_as_dict_sizes(rows):
    cfg = GrouperConfig(key_columns=["role"])
    result = export_groups_as_dict(rows, cfg)
    assert result["sizes"]["('admin',)"] == 2
    assert result["sizes"]["('user',)"] == 3


def test_export_groups_as_dict_groups_contain_rows(rows):
    cfg = GrouperConfig(key_columns=["role"])
    result = export_groups_as_dict(rows, cfg)
    admin_rows = result["groups"]["('admin',)"]
    assert len(admin_rows) == 2


def test_export_group_as_json_returns_string(rows):
    cfg = GrouperConfig(key_columns=["role"])
    output = export_group_as_json(rows, cfg, key=("admin",))
    assert isinstance(output, str)


def test_export_group_as_json_is_valid_json(rows):
    cfg = GrouperConfig(key_columns=["role"])
    output = export_group_as_json(rows, cfg, key=("admin",))
    parsed = json.loads(output)
    assert isinstance(parsed, list)


def test_export_group_as_json_correct_row_count(rows):
    cfg = GrouperConfig(key_columns=["role"])
    output = export_group_as_json(rows, cfg, key=("user",))
    parsed = json.loads(output)
    assert len(parsed) == 3


def test_export_group_as_json_missing_key_returns_empty(rows):
    cfg = GrouperConfig(key_columns=["role"])
    output = export_group_as_json(rows, cfg, key=("moderator",))
    parsed = json.loads(output)
    assert parsed == []


def test_export_largest_group_returns_string(rows):
    cfg = GrouperConfig(key_columns=["role"])
    output = export_largest_group(rows, cfg)
    assert isinstance(output, str)


def test_export_largest_group_is_valid_json(rows):
    cfg = GrouperConfig(key_columns=["role"])
    output = export_largest_group(rows, cfg)
    parsed = json.loads(output)
    assert isinstance(parsed, list)


def test_export_largest_group_correct_count(rows):
    cfg = GrouperConfig(key_columns=["role"])
    output = export_largest_group(rows, cfg)
    parsed = json.loads(output)
    assert len(parsed) == 3


def test_export_largest_group_empty_input():
    cfg = GrouperConfig(key_columns=["role"])
    output = export_largest_group([], cfg)
    assert output == "[]"
