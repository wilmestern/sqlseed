"""Command-line interface for sqlseed."""

from __future__ import annotations

import argparse
import sys
from typing import Optional

from sqlseed.schema_parser import parse_create_table
from sqlseed.seed_planner import plan_seed
from sqlseed.output_writer import write_output


DEFAULT_COUNT = 10
DEFAULT_DIALECT = "postgres"


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    """Parse command-line arguments.

    Args:
        argv: Argument list (defaults to sys.argv[1:]).

    Returns:
        Parsed namespace with schema, count, dialect, output, and no_header.
    """
    parser = argparse.ArgumentParser(
        prog="sqlseed",
        description="Generate realistic SQL fixture data from a schema file.",
    )
    parser.add_argument(
        "schema",
        help="Path to the SQL schema file containing CREATE TABLE statements.",
    )
    parser.add_argument(
        "-n",
        "--count",
        type=int,
        default=DEFAULT_COUNT,
        help=f"Number of rows to generate per table (default: {DEFAULT_COUNT}).",
    )
    parser.add_argument(
        "-d",
        "--dialect",
        default=DEFAULT_DIALECT,
        choices=["postgres", "mysql", "sqlite"],
        help=f"SQL dialect to use (default: {DEFAULT_DIALECT}).",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=None,
        help="Write output to this file instead of stdout.",
    )
    parser.add_argument(
        "--no-header",
        action="store_true",
        default=False,
        help="Omit the auto-generated header comment from output.",
    )
    return parser.parse_args(argv)


def run(argv: Optional[list[str]] = None) -> None:
    """Entry point: parse args, generate seed script, and write output.

    Args:
        argv: Optional argument list for testing.
    """
    args = parse_args(argv)

    try:
        with open(args.schema, "r", encoding="utf-8") as fh:
            schema_sql = fh.read()
    except OSError as exc:
        print(f"sqlseed: error reading schema file: {exc}", file=sys.stderr)
        sys.exit(1)

    sql = plan_seed(schema_sql, count=args.count, dialect=args.dialect)

    write_output(
        sql,
        output_path=args.output,
        include_header=not args.no_header,
    )
