"""Tests for sqlseed.row_normalizer."""

import pytest

from sqlseed.row_normalizer import (
    NormalizerConfig,
    NormalizerError,
    normalize_row,
    normalize_rows,
)


# ---------------------------------------------------------------------------
# NormalizerConfig
# ---------------------------------------------------------------------------

def test_normalizer_config_defaults():
    config = NormalizerConfig()
    assert config.strip_strings is True
    assert config.lowercase_strings is False
    assert config.none_for_empty_strings is False


def test_normalizer_config_add_registers_column():
    config = NormalizerConfig()
    config.add("email", str.lower)
    assert "email" in config.columns()


def test_normalizer_config_add_normalises_column_lowercase():
    config = NormalizerConfig()
    config.add("Email", str.lower)
    assert "email" in config.columns()


def test_normalizer_config_add_empty_column_raises():
    config = NormalizerConfig()
    with pytest.raises(NormalizerError):
        config.add("", str.lower)


def test_normalizer_config_add_non_callable_raises():
    config = NormalizerConfig()
    with pytest.raises(NormalizerError):
        config.add("name", "not_a_function")  # type: ignore[arg-type]


def test_normalizer_config_remove_existing():
    config = NormalizerConfig()
    config.add("status", str.upper)
    config.remove("status")
    assert "status" not in config.columns()


def test_normalizer_config_remove_unknown_does_not_raise():
    config = NormalizerConfig()
    config.remove("nonexistent")  # should not raise


# ---------------------------------------------------------------------------
# normalize_row — global rules
# ---------------------------------------------------------------------------

def test_normalize_row_strips_strings_by_default():
    config = NormalizerConfig()
    row = {"name": "  Alice  ", "age": 30}
    result = normalize_row(row, config)
    assert result["name"] == "Alice"
    assert result["age"] == 30


def test_normalize_row_lowercase_strings():
    config = NormalizerConfig(lowercase_strings=True)
    row = {"email": "USER@EXAMPLE.COM"}
    result = normalize_row(row, config)
    assert result["email"] == "user@example.com"


def test_normalize_row_none_for_empty_strings():
    config = NormalizerConfig(none_for_empty_strings=True)
    row = {"bio": "   "}
    result = normalize_row(row, config)
    assert result["bio"] is None


def test_normalize_row_none_value_unchanged():
    config = NormalizerConfig()
    row = {"bio": None}
    result = normalize_row(row, config)
    assert result["bio"] is None


def test_normalize_row_non_string_unchanged():
    config = NormalizerConfig(lowercase_strings=True)
    row = {"score": 42, "active": True}
    result = normalize_row(row, config)
    assert result["score"] == 42
    assert result["active"] is True


# ---------------------------------------------------------------------------
# normalize_row — per-column rules
# ---------------------------------------------------------------------------

def test_normalize_row_applies_column_rule():
    config = NormalizerConfig(strip_strings=False)
    config.add("code", lambda v: v.upper() if isinstance(v, str) else v)
    row = {"code": "abc"}
    result = normalize_row(row, config)
    assert result["code"] == "ABC"


def test_normalize_row_column_rule_error_raises_normalizer_error():
    config = NormalizerConfig()

    def bad_rule(v: object) -> object:
        raise ValueError("boom")

    config.add("field", bad_rule)
    with pytest.raises(NormalizerError, match="field"):
        normalize_row({"field": "value"}, config)


# ---------------------------------------------------------------------------
# normalize_rows
# ---------------------------------------------------------------------------

def test_normalize_rows_returns_list():
    rows = [{"name": " Alice "}, {"name": " Bob "}]
    result = normalize_rows(rows)
    assert isinstance(result, list)
    assert len(result) == 2


def test_normalize_rows_applies_strip():
    rows = [{"name": "  Carol  "}]
    result = normalize_rows(rows)
    assert result[0]["name"] == "Carol"


def test_normalize_rows_default_config_when_none():
    rows = [{"val": "  x  "}]
    result = normalize_rows(rows, config=None)
    assert result[0]["val"] == "x"


def test_normalize_rows_empty_input():
    result = normalize_rows([])
    assert result == []
