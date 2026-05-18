# sqlseed

A schema-aware SQL fixture generator that produces realistic test data from existing table definitions.

---

## Installation

```bash
pip install sqlseed
```

---

## Usage

Point `sqlseed` at your database, specify a table, and let it generate ready-to-use INSERT statements populated with realistic data.

```python
from sqlseed import Seeder

seeder = Seeder(connection_string="postgresql://user:pass@localhost/mydb")

# Generate 50 rows of realistic fixture data for the "users" table
sql = seeder.generate(table="users", rows=50)

print(sql)
# INSERT INTO users (id, name, email, created_at) VALUES
# (1, 'Alice Morgan', 'alice.morgan@example.com', '2023-04-12 08:31:00'),
# (2, 'James Patel',  'james.patel@example.com',  '2023-06-07 14:55:22'),
# ...

# Write directly to a file
seeder.generate(table="orders", rows=100, output="fixtures/orders.sql")
```

### CLI

```bash
sqlseed --db postgresql://user:pass@localhost/mydb --table users --rows 50 --out fixtures/users.sql
```

### Supported Databases

| Database   | Status |
|------------|--------|
| PostgreSQL | ✅      |
| MySQL      | ✅      |
| SQLite     | ✅      |

---

## Features

- Introspects existing table schemas automatically
- Respects column types, constraints, and foreign keys
- Produces deterministic output with a `--seed` flag
- Outputs plain SQL, JSON, or CSV fixtures

---

## License

This project is licensed under the [MIT License](LICENSE).