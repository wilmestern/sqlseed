"""Tests for sqlseed.value_overrides."""

import pytest

from sqlseed.value_overrides import OverrideRegistry, apply_overrides


# ---------------------------------------------------------------------------
# OverrideRegistry.set / get / has
# ---------------------------------------------------------------------------

def test_set_and_get_returns_value():
    reg = OverrideRegistry()
    reg.set("users", "email", "test@example.com")
    assert reg.get("users", "email") == "test@example.com"


def test_has_returns_true_when_set():
    reg = OverrideRegistry()
    reg.set("users", "id", 42)
    assert reg.has("users", "id") is True


def test_has_returns_false_when_not_set():
    reg = OverrideRegistry()
    assert reg.has("users", "email") is False


def test_get_returns_none_when_missing():
    reg = OverrideRegistry()
    assert reg.get("orders", "total") is None


def test_set_is_case_insensitive_for_table():
    reg = OverrideRegistry()
    reg.set("Users", "Email", "a@b.com")
    assert reg.get("users", "email") == "a@b.com"


def test_has_with_none_value_still_returns_true():
    """An override of None is still a valid explicit override."""
    reg = OverrideRegistry()
    reg.set("users", "deleted_at", None)
    assert reg.has("users", "deleted_at") is True
    assert reg.get("users", "deleted_at") is None


# ---------------------------------------------------------------------------
# OverrideRegistry.clear
# ---------------------------------------------------------------------------

def test_clear_all_removes_everything():
    reg = OverrideRegistry()
    reg.set("users", "id", 1)
    reg.set("posts", "title", "Hello")
    reg.clear()
    assert reg.has("users", "id") is False
    assert reg.has("posts", "title") is False


def test_clear_table_only_removes_that_table():
    reg = OverrideRegistry()
    reg.set("users", "id", 1)
    reg.set("posts", "title", "Hello")
    reg.clear(table="users")
    assert reg.has("users", "id") is False
    assert reg.has("posts", "title") is True


# ---------------------------------------------------------------------------
# OverrideRegistry.all_for_table
# ---------------------------------------------------------------------------

def test_all_for_table_returns_correct_columns():
    reg = OverrideRegistry()
    reg.set("users", "id", 7)
    reg.set("users", "email", "x@y.com")
    reg.set("posts", "id", 99)
    result = reg.all_for_table("users")
    assert result == {"id": 7, "email": "x@y.com"}


def test_all_for_table_empty_when_none_registered():
    reg = OverrideRegistry()
    assert reg.all_for_table("nonexistent") == {}


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def test_set_empty_table_raises():
    reg = OverrideRegistry()
    with pytest.raises(ValueError, match="table"):
        reg.set("", "col", 1)


def test_set_empty_column_raises():
    reg = OverrideRegistry()
    with pytest.raises(ValueError, match="column"):
        reg.set("users", "", 1)


# ---------------------------------------------------------------------------
# apply_overrides
# ---------------------------------------------------------------------------

def test_apply_overrides_replaces_value():
    reg = OverrideRegistry()
    reg.set("users", "email", "fixed@example.com")
    row = {"id": 1, "email": "random@gen.com", "name": "Alice"}
    result = apply_overrides(row, "users", reg)
    assert result["email"] == "fixed@example.com"


def test_apply_overrides_does_not_mutate_original():
    reg = OverrideRegistry()
    reg.set("users", "email", "fixed@example.com")
    row = {"email": "original@gen.com"}
    apply_overrides(row, "users", reg)
    assert row["email"] == "original@gen.com"


def test_apply_overrides_no_overrides_returns_same_values():
    reg = OverrideRegistry()
    row = {"id": 5, "name": "Bob"}
    result = apply_overrides(row, "users", reg)
    assert result == {"id": 5, "name": "Bob"}
