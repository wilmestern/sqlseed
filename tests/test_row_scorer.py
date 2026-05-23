"""Tests for RowScorer and built-in scoring rules."""

import pytest

from sqlseed.row_scorer import RowScorer, ScoreResult
from sqlseed.scoring_rules import completeness_rule, string_length_rule, no_placeholder_rule, numeric_range_rule
from sqlseed.schema_parser import TableDefinition, ColumnDefinition


@pytest.fixture()
def simple_table() -> TableDefinition:
    return TableDefinition(
        name="users",
        columns=[
            ColumnDefinition(name="id", data_type="INTEGER", nullable=False, primary_key=True),
            ColumnDefinition(name="username", data_type="VARCHAR", nullable=False, max_length=50),
            ColumnDefinition(name="email", data_type="VARCHAR", nullable=True, max_length=100),
            ColumnDefinition(name="score", data_type="FLOAT", nullable=True),
        ],
    )


@pytest.fixture()
def scorer() -> RowScorer:
    return RowScorer()


def test_add_rule_registers_name(scorer, simple_table):
    scorer.add_rule("completeness", completeness_rule)
    assert "completeness" in scorer.rule_names()


def test_add_duplicate_rule_raises(scorer):
    scorer.add_rule("r", completeness_rule)
    with pytest.raises(ValueError, match="already registered"):
        scorer.add_rule("r", completeness_rule)


def test_add_non_callable_raises(scorer):
    with pytest.raises(TypeError):
        scorer.add_rule("bad", "not_a_function")  # type: ignore


def test_add_non_positive_weight_raises(scorer):
    with pytest.raises(ValueError, match="positive"):
        scorer.add_rule("w", completeness_rule, weight=0)


def test_remove_rule(scorer):
    scorer.add_rule("r", completeness_rule)
    scorer.remove_rule("r")
    assert "r" not in scorer.rule_names()


def test_remove_unknown_rule_does_not_raise(scorer):
    scorer.remove_rule("nonexistent")


def test_clear_removes_all_rules(scorer):
    scorer.add_rule("a", completeness_rule)
    scorer.add_rule("b", string_length_rule)
    scorer.clear()
    assert scorer.rule_names() == []


def test_score_no_rules_returns_zero(scorer, simple_table):
    result = scorer.score({"id": 1}, simple_table)
    assert result.total == 0.0


def test_score_returns_score_result(scorer, simple_table):
    scorer.add_rule("completeness", completeness_rule)
    result = scorer.score({"id": 1, "username": "alice", "email": "a@b.com", "score": 9.5}, simple_table)
    assert isinstance(result, ScoreResult)
    assert 0.0 <= result.total <= 1.0


def test_completeness_all_present(simple_table):
    row = {"id": 1, "username": "alice", "email": "a@b.com", "score": 5.0}
    assert completeness_rule(row, simple_table) == 1.0


def test_completeness_partial(simple_table):
    row = {"id": 1, "username": "alice", "email": None, "score": None}
    assert completeness_rule(row, simple_table) == pytest.approx(0.5)


def test_string_length_rule_valid(simple_table):
    row = {"id": 1, "username": "alice", "email": "a@b.com", "score": 1.0}
    assert string_length_rule(row, simple_table) == 1.0


def test_string_length_rule_exceeds_max(simple_table):
    row = {"id": 1, "username": "a" * 200, "email": "a@b.com", "score": 1.0}
    result = string_length_rule(row, simple_table)
    assert result < 1.0


def test_no_placeholder_rule_clean_row(simple_table):
    row = {"id": 1, "username": "alice", "email": "a@b.com", "score": 5.0}
    assert no_placeholder_rule(row, simple_table) == 1.0


def test_no_placeholder_rule_detects_placeholder(simple_table):
    row = {"id": 1, "username": "N/A", "email": "a@b.com", "score": 5.0}
    assert no_placeholder_rule(row, simple_table) < 1.0


def test_numeric_range_rule_valid(simple_table):
    row = {"id": 1, "username": "alice", "email": None, "score": 3.14}
    assert numeric_range_rule(row, simple_table) == 1.0


def test_filter_by_score_returns_high_quality_rows(scorer, simple_table):
    scorer.add_rule("completeness", completeness_rule)
    rows = [
        {"id": 1, "username": "alice", "email": "a@b.com", "score": 1.0},
        {"id": 2, "username": None, "email": None, "score": None},
    ]
    filtered = scorer.filter_by_score(rows, simple_table, threshold=0.9)
    assert len(filtered) == 1
    assert filtered[0]["id"] == 1
