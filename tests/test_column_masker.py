"""Tests for sqlseed.column_masker."""

import pytest

from sqlseed.column_masker import ColumnMasker, hash_mask, partial_mask, redact


@pytest.fixture()
def masker() -> ColumnMasker:
    return ColumnMasker()


# ---------------------------------------------------------------------------
# ColumnMasker.add / names / is_masked
# ---------------------------------------------------------------------------

def test_add_registers_mask(masker: ColumnMasker) -> None:
    masker.add("email", redact())
    assert masker.is_masked("email")


def test_add_is_case_insensitive(masker: ColumnMasker) -> None:
    masker.add("Email", redact())
    assert masker.is_masked("email")
    assert masker.is_masked("EMAIL")


def test_add_non_callable_raises(masker: ColumnMasker) -> None:
    with pytest.raises(TypeError, match="callable"):
        masker.add("email", "not_a_function")  # type: ignore[arg-type]


def test_names_returns_all_masked_columns(masker: ColumnMasker) -> None:
    masker.add("email", redact())
    masker.add("phone", redact())
    assert sorted(masker.names()) == ["email", "phone"]


# ---------------------------------------------------------------------------
# ColumnMasker.remove / clear
# ---------------------------------------------------------------------------

def test_remove_unregisters_mask(masker: ColumnMasker) -> None:
    masker.add("email", redact())
    masker.remove("email")
    assert not masker.is_masked("email")


def test_remove_unknown_does_not_raise(masker: ColumnMasker) -> None:
    masker.remove("nonexistent")  # should not raise


def test_clear_removes_all(masker: ColumnMasker) -> None:
    masker.add("email", redact())
    masker.add("phone", redact())
    masker.clear()
    assert masker.names() == []


# ---------------------------------------------------------------------------
# ColumnMasker.apply
# ---------------------------------------------------------------------------

def test_apply_returns_masked_value(masker: ColumnMasker) -> None:
    masker.add("email", redact("REDACTED"))
    assert masker.apply("email", "user@example.com") == "REDACTED"


def test_apply_returns_original_when_not_masked(masker: ColumnMasker) -> None:
    assert masker.apply("username", "alice") == "alice"


# ---------------------------------------------------------------------------
# ColumnMasker.mask_row
# ---------------------------------------------------------------------------

def test_mask_row_applies_masks_to_matching_columns(masker: ColumnMasker) -> None:
    masker.add("email", redact())
    row = {"id": 1, "email": "user@example.com", "username": "alice"}
    result = masker.mask_row(row)
    assert result["email"] == "***"
    assert result["id"] == 1
    assert result["username"] == "alice"


def test_mask_row_returns_new_dict(masker: ColumnMasker) -> None:
    masker.add("email", redact())
    row = {"email": "user@example.com"}
    result = masker.mask_row(row)
    assert result is not row


# ---------------------------------------------------------------------------
# Built-in mask factories
# ---------------------------------------------------------------------------

def test_redact_default_placeholder() -> None:
    fn = redact()
    assert fn("anything") == "***"


def test_redact_custom_placeholder() -> None:
    fn = redact("[hidden]")
    assert fn(42) == "[hidden]"


def test_partial_mask_hides_tail() -> None:
    fn = partial_mask(visible_chars=3)
    assert fn("secret") == "sec***"


def test_partial_mask_short_value_unchanged() -> None:
    fn = partial_mask(visible_chars=10)
    assert fn("hi") == "hi"


def test_hash_mask_returns_16_char_hex() -> None:
    fn = hash_mask()
    result = fn("password123")
    assert len(result) == 16
    assert all(c in "0123456789abcdef" for c in result)


def test_hash_mask_deterministic() -> None:
    fn = hash_mask()
    assert fn("same") == fn("same")
