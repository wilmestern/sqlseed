"""Tests for sqlseed.row_redactor."""
import pytest

from sqlseed.row_redactor import (
    RedactorConfig,
    RedactorError,
    redact_row,
    redact_rows,
)


# ---------------------------------------------------------------------------
# RedactorConfig construction
# ---------------------------------------------------------------------------

def test_redactor_config_default_mask():
    cfg = RedactorConfig()
    assert cfg.default_mask == "***REDACTED***"


def test_redactor_config_empty_default_mask_raises():
    with pytest.raises(RedactorError):
        RedactorConfig(default_mask="")


def test_redactor_config_custom_mask():
    cfg = RedactorConfig(default_mask="[hidden]")
    assert cfg.default_mask == "[hidden]"


# ---------------------------------------------------------------------------
# add / remove / clear / names / has
# ---------------------------------------------------------------------------

def test_add_registers_column():
    cfg = RedactorConfig()
    cfg.add("email")
    assert cfg.has("email")


def test_add_empty_column_raises():
    cfg = RedactorConfig()
    with pytest.raises(RedactorError):
        cfg.add("")


def test_add_non_callable_mask_raises():
    cfg = RedactorConfig()
    with pytest.raises(RedactorError):
        cfg.add("email", mask="not-callable")  # type: ignore[arg-type]


def test_add_callable_mask_accepted():
    cfg = RedactorConfig()
    cfg.add("phone", mask=lambda v: "XXX")
    assert cfg.has("phone")


def test_names_returns_registered_columns():
    cfg = RedactorConfig()
    cfg.add("email")
    cfg.add("ssn")
    assert set(cfg.names()) == {"email", "ssn"}


def test_remove_existing_column():
    cfg = RedactorConfig()
    cfg.add("email")
    cfg.remove("email")
    assert not cfg.has("email")


def test_remove_unknown_column_does_not_raise():
    cfg = RedactorConfig()
    cfg.remove("nonexistent")  # should not raise


def test_clear_removes_all_rules():
    cfg = RedactorConfig()
    cfg.add("email")
    cfg.add("phone")
    cfg.clear()
    assert cfg.names() == []


def test_add_is_case_insensitive_by_default():
    cfg = RedactorConfig()
    cfg.add("Email")
    assert cfg.has("email")
    assert cfg.has("EMAIL")


def test_add_case_sensitive_mode():
    cfg = RedactorConfig(case_sensitive=True)
    cfg.add("Email")
    assert cfg.has("Email")
    assert not cfg.has("email")


# ---------------------------------------------------------------------------
# redact_row
# ---------------------------------------------------------------------------

def test_redact_row_replaces_registered_column():
    cfg = RedactorConfig(default_mask="[HIDDEN]")
    cfg.add("password")
    row = {"id": 1, "password": "secret"}
    result = redact_row(row, cfg)
    assert result["password"] == "[HIDDEN]"
    assert result["id"] == 1


def test_redact_row_callable_mask_receives_original_value():
    seen = []
    cfg = RedactorConfig()
    cfg.add("salary", mask=lambda v: (seen.append(v), "[REDACTED]")[1])
    row = {"salary": 50000}
    redact_row(row, cfg)
    assert seen == [50000]


def test_redact_row_unregistered_columns_unchanged():
    cfg = RedactorConfig()
    cfg.add("email")
    row = {"id": 42, "name": "Alice", "email": "alice@example.com"}
    result = redact_row(row, cfg)
    assert result["id"] == 42
    assert result["name"] == "Alice"


def test_redact_row_returns_new_dict():
    cfg = RedactorConfig()
    cfg.add("email")
    row = {"email": "alice@example.com"}
    result = redact_row(row, cfg)
    assert result is not row


# ---------------------------------------------------------------------------
# redact_rows
# ---------------------------------------------------------------------------

def test_redact_rows_applies_to_all_rows():
    cfg = RedactorConfig(default_mask="XXX")
    cfg.add("token")
    rows = [{"token": "abc"}, {"token": "def"}, {"token": "ghi"}]
    result = redact_rows(rows, cfg)
    assert all(r["token"] == "XXX" for r in result)


def test_redact_rows_empty_input_returns_empty():
    cfg = RedactorConfig()
    assert redact_rows([], cfg) == []


def test_redact_rows_no_rules_returns_unchanged_values():
    cfg = RedactorConfig()
    rows = [{"id": 1, "name": "Bob"}]
    result = redact_rows(rows, cfg)
    assert result[0]["name"] == "Bob"
