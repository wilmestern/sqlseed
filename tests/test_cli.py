"""Tests for sqlseed.cli module."""

import os
import tempfile
import pytest
from sqlseed.cli import run, parse_args


SAMPLE_SCHEMA = """
CREATE TABLE products (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    price DECIMAL(10,2),
    created_at DATE
);
"""


@pytest.fixture
def schema_file(tmp_path):
    path = tmp_path / "schema.sql"
    path.write_text(SAMPLE_SCHEMA)
    return str(path)


def test_parse_args_defaults(schema_file):
    args = parse_args([schema_file])
    assert args.schema_file == schema_file
    assert args.count == 10
    assert args.output is None


def test_parse_args_custom_count(schema_file):
    args = parse_args([schema_file, "-n", "5"])
    assert args.count == 5


def test_parse_args_output_flag(schema_file, tmp_path):
    out = str(tmp_path / "out.sql")
    args = parse_args([schema_file, "-o", out])
    assert args.output == out


def test_run_outputs_inserts(schema_file, capsys):
    run([schema_file, "-n", "3"])
    captured = capsys.readouterr()
    assert "INSERT INTO products" in captured.out
    assert captured.out.count("INSERT INTO products") == 3


def test_run_writes_output_file(schema_file, tmp_path):
    out_path = str(tmp_path / "seed.sql")
    run([schema_file, "-n", "2", "-o", out_path])
    assert os.path.exists(out_path)
    content = open(out_path).read()
    assert "INSERT INTO products" in content
    assert content.count("INSERT INTO products") == 2


def test_run_exits_on_missing_file():
    with pytest.raises(SystemExit) as exc_info:
        run(["nonexistent_file.sql"])
    assert exc_info.value.code == 1


def test_run_exits_on_no_create_table(tmp_path):
    bad_file = tmp_path / "bad.sql"
    bad_file.write_text("SELECT 1;")
    with pytest.raises(SystemExit) as exc_info:
        run([str(bad_file)])
    assert exc_info.value.code == 1
