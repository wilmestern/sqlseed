"""Command-line interface for sqlseed."""

import argparse
import sys
from sqlseed.schema_parser import parse_create_table
from sqlseed.insert_generator import generate_seed_script


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        prog="sqlseed",
        description="Generate realistic SQL INSERT statements from CREATE TABLE definitions.",
    )
    parser.add_argument(
        "schema_file",
        help="Path to a .sql file containing CREATE TABLE statements.",
    )
    parser.add_argument(
        "-n", "--count",
        type=int,
        default=10,
        help="Number of rows to generate per table (default: 10).",
    )
    parser.add_argument(
        "-o", "--output",
        default=None,
        help="Output file path. Defaults to stdout.",
    )
    return parser.parse_args(argv)


def run(argv=None):
    args = parse_args(argv)

    try:
        with open(args.schema_file, "r") as fh:
            schema_sql = fh.read()
    except FileNotFoundError:
        print(f"Error: schema file '{args.schema_file}' not found.", file=sys.stderr)
        sys.exit(1)

    # Split on semicolons to handle multiple CREATE TABLE statements
    statements = [s.strip() for s in schema_sql.split(";") if s.strip()]
    tables = []
    for stmt in statements:
        if stmt.upper().startswith("CREATE TABLE"):
            try:
                tables.append(parse_create_table(stmt))
            except Exception as exc:
                print(f"Warning: could not parse statement: {exc}", file=sys.stderr)

    if not tables:
        print("Error: no valid CREATE TABLE statements found.", file=sys.stderr)
        sys.exit(1)

    script = generate_seed_script(tables, count=args.count)

    if args.output:
        with open(args.output, "w") as fh:
            fh.write(script + "\n")
        print(f"Seed script written to {args.output}")
    else:
        print(script)


if __name__ == "__main__":
    run()
