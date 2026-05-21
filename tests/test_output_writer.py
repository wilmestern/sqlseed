"""Tests for sqlseed.output_writer module."""

from __future__ import annotations

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from sqlseed.output_writer import (
    SQL_HEADER,
    SQL_SEPARATOR,
    build_output,
    write_to_file,
    write_to_stdout,
    write_output,
)


SAMPLE_SQL = "INSERT INTO users (id) VALUES (1);"


# --- build_output ---

def test_build_output_includes_header_by_default():
    result = build_output(SAMPLE_SQL)
    assert result.startswith(SQL_HEADER)


def test_build_output_includes_separator():
    result = build_output(SAMPLE_SQL)
    assert SQL_SEPARATOR in result


def test_build_output_contains_sql():
    result = build_output(SAMPLE_SQL)
    assert SAMPLE_SQL in result


def test_build_output_no_header():
    result = build_output(SAMPLE_SQL, include_header=False)
    assert not result.startswith(SQL_HEADER)
    assert SAMPLE_SQL in result


def test_build_output_ends_with_newline():
    result = build_output(SAMPLE_SQL)
    assert result.endswith("\n")


def test_build_output_strips_extra_whitespace():
    padded = "   " + SAMPLE_SQL + "   "
    result = build_output(padded, include_header=False)
    assert result == SAMPLE_SQL + "\n"


# --- write_to_file ---

def test_write_to_file_creates_file(tmp_path):
    dest = tmp_path / "output" / "seed.sql"
    write_to_file(SAMPLE_SQL, str(dest))
    assert dest.exists()
    assert dest.read_text(encoding="utf-8") == SAMPLE_SQL


def test_write_to_file_creates_parent_directories(tmp_path):
    dest = tmp_path / "deep" / "nested" / "seed.sql"
    write_to_file(SAMPLE_SQL, str(dest))
    assert dest.exists()


def test_write_to_file_respects_encoding(tmp_path):
    dest = tmp_path / "seed.sql"
    content = "-- café\n" + SAMPLE_SQL
    write_to_file(content, str(dest), encoding="utf-8")
    assert dest.read_text(encoding="utf-8") == content


# --- write_to_stdout ---

def test_write_to_stdout_calls_stdout_write(capsys):
    write_to_stdout(SAMPLE_SQL)
    captured = capsys.readouterr()
    assert captured.out == SAMPLE_SQL


# --- write_output ---

def test_write_output_to_stdout_when_no_path(capsys):
    write_output(SAMPLE_SQL, output_path=None, include_header=False)
    captured = capsys.readouterr()
    assert SAMPLE_SQL in captured.out


def test_write_output_to_file(tmp_path):
    dest = tmp_path / "seed.sql"
    write_output(SAMPLE_SQL, output_path=str(dest), include_header=False)
    assert dest.exists()
    assert SAMPLE_SQL in dest.read_text(encoding="utf-8")


def test_write_output_with_header_to_file(tmp_path):
    dest = tmp_path / "seed.sql"
    write_output(SAMPLE_SQL, output_path=str(dest), include_header=True)
    content = dest.read_text(encoding="utf-8")
    assert SQL_HEADER in content
