"""Tests for sqlseed.row_transformer."""

import pytest

from sqlseed.row_transformer import (
    RowTransformer,
    mask_column,
    transform_rows,
    uppercase_strings,
)


@pytest.fixture()
def transformer() -> RowTransformer:
    return RowTransformer()


def test_add_registers_transform(transformer: RowTransformer) -> None:
    transformer.add("upper", uppercase_strings)
    assert "upper" in transformer.names()


def test_add_non_callable_raises(transformer: RowTransformer) -> None:
    with pytest.raises(TypeError, match="callable"):
        transformer.add("bad", "not_a_function")  # type: ignore[arg-type]


def test_remove_existing(transformer: RowTransformer) -> None:
    transformer.add("upper", uppercase_strings)
    transformer.remove("upper")
    assert "upper" not in transformer.names()


def test_remove_unknown_does_not_raise(transformer: RowTransformer) -> None:
    transformer.remove("nonexistent")  # should not raise


def test_clear_removes_all(transformer: RowTransformer) -> None:
    transformer.add("a", uppercase_strings)
    transformer.add("b", uppercase_strings)
    transformer.clear()
    assert transformer.names() == []


def test_apply_uppercase_strings(transformer: RowTransformer) -> None:
    transformer.add("upper", uppercase_strings)
    row = {"name": "alice", "age": 30}
    result = transformer.apply(row)
    assert result["name"] == "ALICE"
    assert result["age"] == 30


def test_apply_does_not_mutate_original(transformer: RowTransformer) -> None:
    transformer.add("upper", uppercase_strings)
    row = {"name": "alice"}
    transformer.apply(row)
    assert row["name"] == "alice"


def test_apply_no_transforms_returns_copy(transformer: RowTransformer) -> None:
    row = {"x": 1, "y": "hello"}
    result = transformer.apply(row)
    assert result == row
    assert result is not row


def test_mask_column_replaces_value(transformer: RowTransformer) -> None:
    transformer.add("mask_email", mask_column("email"))
    row = {"email": "user@example.com", "name": "Bob"}
    result = transformer.apply(row)
    assert result["email"] == "***"
    assert result["name"] == "Bob"


def test_mask_column_custom_mask(transformer: RowTransformer) -> None:
    transformer.add("mask_pw", mask_column("password", mask="[REDACTED]"))
    row = {"password": "secret123"}
    result = transformer.apply(row)
    assert result["password"] == "[REDACTED]"


def test_mask_column_none_value_unchanged(transformer: RowTransformer) -> None:
    transformer.add("mask_email", mask_column("email"))
    row = {"email": None}
    result = transformer.apply(row)
    assert result["email"] is None


def test_mask_column_case_insensitive(transformer: RowTransformer) -> None:
    transformer.add("mask", mask_column("Email"))
    row = {"email": "x@y.com"}
    result = transformer.apply(row)
    assert result["email"] == "***"


def test_transform_rows_applies_to_all(transformer: RowTransformer) -> None:
    transformer.add("upper", uppercase_strings)
    rows = [{"name": "alice"}, {"name": "bob"}, {"name": "carol"}]
    results = transform_rows(rows, transformer)
    assert [r["name"] for r in results] == ["ALICE", "BOB", "CAROL"]


def test_transform_rows_empty_list(transformer: RowTransformer) -> None:
    assert transform_rows([], transformer) == []
