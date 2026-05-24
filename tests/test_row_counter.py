"""Tests for sqlseed.row_counter."""

import pytest
from sqlseed.row_counter import CounterError, RowCounter, TableCount


@pytest.fixture
def counter() -> RowCounter:
    c = RowCounter()
    c.register("users", 10)
    c.register("posts", 5)
    return c


def test_register_creates_table_count(counter: RowCounter) -> None:
    tc = counter.get("users")
    assert tc is not None
    assert tc.table_name == "users"
    assert tc.expected == 10
    assert tc.actual == 0


def test_register_negative_expected_raises() -> None:
    c = RowCounter()
    with pytest.raises(CounterError, match="non-negative"):
        c.register("users", -1)


def test_increment_increases_actual(counter: RowCounter) -> None:
    counter.increment("users", 3)
    tc = counter.get("users")
    assert tc is not None
    assert tc.actual == 3


def test_increment_default_amount(counter: RowCounter) -> None:
    counter.increment("users")
    tc = counter.get("users")
    assert tc is not None
    assert tc.actual == 1


def test_increment_unregistered_table_raises(counter: RowCounter) -> None:
    with pytest.raises(CounterError, match="not registered"):
        counter.increment("comments")


def test_increment_negative_amount_raises(counter: RowCounter) -> None:
    with pytest.raises(CounterError, match="non-negative"):
        counter.increment("users", -2)


def test_get_returns_none_for_unknown_table(counter: RowCounter) -> None:
    assert counter.get("nonexistent") is None


def test_get_is_case_insensitive(counter: RowCounter) -> None:
    counter.increment("USERS", 5)
    tc = counter.get("users")
    assert tc is not None
    assert tc.actual == 5


def test_table_count_is_complete_when_actual_meets_expected() -> None:
    tc = TableCount(table_name="t", expected=5, actual=5)
    assert tc.is_complete is True


def test_table_count_is_complete_when_actual_exceeds_expected() -> None:
    tc = TableCount(table_name="t", expected=3, actual=10)
    assert tc.is_complete is True


def test_table_count_not_complete_when_actual_less_than_expected() -> None:
    tc = TableCount(table_name="t", expected=10, actual=4)
    assert tc.is_complete is False
    assert tc.missing == 6


def test_table_count_str_ok(counter: RowCounter) -> None:
    counter.increment("users", 10)
    tc = counter.get("users")
    assert tc is not None
    assert "OK" in str(tc)


def test_table_count_str_missing(counter: RowCounter) -> None:
    counter.increment("users", 3)
    tc = counter.get("users")
    assert tc is not None
    assert "MISSING" in str(tc)


def test_all_complete_false_initially(counter: RowCounter) -> None:
    assert counter.all_complete() is False


def test_all_complete_true_when_all_met(counter: RowCounter) -> None:
    counter.increment("users", 10)
    counter.increment("posts", 5)
    assert counter.all_complete() is True


def test_incomplete_tables_lists_unfinished(counter: RowCounter) -> None:
    counter.increment("users", 10)
    incomplete = counter.incomplete_tables()
    assert len(incomplete) == 1
    assert incomplete[0].table_name == "posts"


def test_summary_returns_all_tables(counter: RowCounter) -> None:
    s = counter.summary()
    assert "users" in s
    assert "posts" in s


def test_reset_clears_actual(counter: RowCounter) -> None:
    counter.increment("users", 7)
    counter.reset("users")
    tc = counter.get("users")
    assert tc is not None
    assert tc.actual == 0


def test_reset_all_clears_all(counter: RowCounter) -> None:
    counter.increment("users", 10)
    counter.increment("posts", 5)
    counter.reset_all()
    assert counter.get("users").actual == 0  # type: ignore[union-attr]
    assert counter.get("posts").actual == 0  # type: ignore[union-attr]
