"""Tests for sqlseed.row_hooks."""
import pytest
from sqlseed.row_hooks import RowHooks


@pytest.fixture()
def hooks():
    return RowHooks()


def test_before_registers_hook(hooks):
    hooks.before("stamp", lambda t, r: r)
    assert "stamp" in hooks.before_names()


def test_after_registers_hook(hooks):
    hooks.after("stamp", lambda t, r: r)
    assert "stamp" in hooks.after_names()


def test_before_non_callable_raises(hooks):
    with pytest.raises(TypeError):
        hooks.before("bad", "not_a_function")  # type: ignore


def test_after_non_callable_raises(hooks):
    with pytest.raises(TypeError):
        hooks.after("bad", 42)  # type: ignore


def test_remove_before(hooks):
    hooks.before("x", lambda t, r: r)
    hooks.remove_before("x")
    assert "x" not in hooks.before_names()


def test_remove_after(hooks):
    hooks.after("x", lambda t, r: r)
    hooks.remove_after("x")
    assert "x" not in hooks.after_names()


def test_remove_unknown_before_does_not_raise(hooks):
    hooks.remove_before("nonexistent")  # should not raise


def test_remove_unknown_after_does_not_raise(hooks):
    hooks.remove_after("nonexistent")  # should not raise


def test_clear_removes_all(hooks):
    hooks.before("a", lambda t, r: r)
    hooks.after("b", lambda t, r: r)
    hooks.clear()
    assert hooks.before_names() == []
    assert hooks.after_names() == []


def test_run_before_mutates_row(hooks):
    hooks.before("add_source", lambda t, r: {**r, "source": "test"})
    result = hooks.run_before("users", {})
    assert result["source"] == "test"


def test_run_after_mutates_row(hooks):
    hooks.after("uppercase_name", lambda t, r: {**r, "name": "ALICE"})
    result = hooks.run_after("users", {"name": "alice"})
    assert result["name"] == "ALICE"


def test_run_before_passes_table_name(hooks):
    seen = []
    hooks.before("capture", lambda t, r: seen.append(t) or r)
    hooks.run_before("orders", {})
    assert seen == ["orders"]


def test_run_after_passes_table_name(hooks):
    seen = []
    hooks.after("capture", lambda t, r: seen.append(t) or r)
    hooks.run_after("products", {})
    assert seen == ["products"]


def test_run_before_chains_multiple_hooks(hooks):
    hooks.before("step1", lambda t, r: {**r, "a": 1})
    hooks.before("step2", lambda t, r: {**r, "b": 2})
    result = hooks.run_before("t", {})
    assert result["a"] == 1
    assert result["b"] == 2


def test_run_before_none_return_keeps_previous_row(hooks):
    """A hook returning None should not replace the row."""
    hooks.before("noop", lambda t, r: None)
    result = hooks.run_before("t", {"x": 99})
    assert result["x"] == 99
