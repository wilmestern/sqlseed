"""Tests for RowValidatorPipeline and build_default_pipeline."""

import pytest
from sqlseed.schema_parser import TableDefinition, ColumnDefinition
from sqlseed.constraint_validator import UniquenessTracker
from sqlseed.row_validator_pipeline import (
    RowValidatorPipeline,
    PipelineResult,
    build_default_pipeline,
)


@pytest.fixture
def simple_table():
    return TableDefinition(
        name="users",
        columns=[
            ColumnDefinition(name="id", col_type="INTEGER", nullable=False, primary_key=True),
            ColumnDefinition(name="email", col_type="VARCHAR", nullable=False, primary_key=False),
            ColumnDefinition(name="bio", col_type="TEXT", nullable=True, primary_key=False),
        ],
    )


@pytest.fixture
def pipeline():
    return RowValidatorPipeline()


def test_pipeline_result_bool_true_when_passed():
    result = PipelineResult(row={}, passed=True)
    assert bool(result) is True


def test_pipeline_result_bool_false_when_failed():
    result = PipelineResult(row={}, passed=False, errors=["oops"])
    assert bool(result) is False


def test_add_step_registers_name(pipeline):
    pipeline.add_step("my_check", lambda t, r: None)
    assert "my_check" in pipeline.step_names()


def test_add_non_callable_raises(pipeline):
    with pytest.raises(TypeError):
        pipeline.add_step("bad", "not_a_function")


def test_remove_step_removes_by_name(pipeline):
    pipeline.add_step("alpha", lambda t, r: None)
    pipeline.remove_step("alpha")
    assert "alpha" not in pipeline.step_names()


def test_remove_unknown_step_does_not_raise(pipeline):
    pipeline.remove_step("ghost")  # should not raise


def test_run_passes_when_no_errors(pipeline, simple_table):
    pipeline.add_step("ok", lambda t, r: None)
    result = pipeline.run(simple_table, {"id": 1, "email": "a@b.com", "bio": None})
    assert result.passed is True
    assert result.errors == []


def test_run_collects_error_message(pipeline, simple_table):
    pipeline.add_step("fail", lambda t, r: "something went wrong")
    result = pipeline.run(simple_table, {})
    assert result.passed is False
    assert any("something went wrong" in e for e in result.errors)


def test_run_prefixes_error_with_step_name(pipeline, simple_table):
    pipeline.add_step("my_step", lambda t, r: "bad value")
    result = pipeline.run(simple_table, {})
    assert result.errors[0].startswith("[my_step]")


def test_run_accumulates_multiple_errors(pipeline, simple_table):
    pipeline.add_step("s1", lambda t, r: "err1")
    pipeline.add_step("s2", lambda t, r: "err2")
    result = pipeline.run(simple_table, {})
    assert len(result.errors) == 2


def test_build_default_pipeline_has_expected_steps(simple_table):
    p = build_default_pipeline()
    names = p.step_names()
    assert "nullable" in names
    assert "type" in names
    assert "uniqueness" in names


def test_default_pipeline_passes_valid_row(simple_table):
    tracker = UniquenessTracker()
    p = build_default_pipeline(tracker)
    row = {"id": 1, "email": "user@example.com", "bio": None}
    result = p.run(simple_table, row)
    assert result.passed


def test_default_pipeline_fails_null_non_nullable(simple_table):
    p = build_default_pipeline()
    row = {"id": 1, "email": None, "bio": None}
    result = p.run(simple_table, row)
    assert not result.passed
    assert any("email" in e for e in result.errors)


def test_default_pipeline_fails_wrong_type(simple_table):
    p = build_default_pipeline()
    row = {"id": "not-an-int", "email": "x@y.com", "bio": None}
    result = p.run(simple_table, row)
    assert not result.passed
