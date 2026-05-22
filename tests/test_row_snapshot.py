"""Tests for sqlseed.row_snapshot."""

from __future__ import annotations

import pytest

from sqlseed.row_snapshot import Snapshot, SnapshotStore, diff_snapshots


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def store() -> SnapshotStore:
    return SnapshotStore()


_ROWS = [
    {"id": 1, "name": "Alice"},
    {"id": 2, "name": "Bob"},
]


# ---------------------------------------------------------------------------
# SnapshotStore.save
# ---------------------------------------------------------------------------

def test_save_returns_snapshot(store):
    snap = store.save("s1", "users", _ROWS)
    assert isinstance(snap, Snapshot)


def test_save_stores_by_name(store):
    store.save("s1", "users", _ROWS)
    assert "s1" in store.names()


def test_save_empty_name_raises(store):
    with pytest.raises(ValueError, match="empty"):
        store.save("", "users", _ROWS)


def test_save_makes_copy_of_rows(store):
    rows = [{"id": 1}]
    store.save("s1", "users", rows)
    rows.append({"id": 2})
    assert len(store.load("s1").rows) == 1


# ---------------------------------------------------------------------------
# SnapshotStore.load
# ---------------------------------------------------------------------------

def test_load_returns_snapshot(store):
    store.save("s1", "users", _ROWS)
    snap = store.load("s1")
    assert snap is not None
    assert snap.name == "s1"


def test_load_missing_returns_none(store):
    assert store.load("nonexistent") is None


# ---------------------------------------------------------------------------
# SnapshotStore.delete / clear
# ---------------------------------------------------------------------------

def test_delete_removes_snapshot(store):
    store.save("s1", "users", _ROWS)
    store.delete("s1")
    assert store.load("s1") is None


def test_delete_unknown_does_not_raise(store):
    store.delete("ghost")  # should not raise


def test_clear_removes_all(store):
    store.save("s1", "users", _ROWS)
    store.save("s2", "posts", _ROWS)
    store.clear()
    assert store.names() == []


# ---------------------------------------------------------------------------
# Snapshot.__len__
# ---------------------------------------------------------------------------

def test_snapshot_len(store):
    snap = store.save("s1", "users", _ROWS)
    assert len(snap) == 2


# ---------------------------------------------------------------------------
# diff_snapshots
# ---------------------------------------------------------------------------

def test_diff_snapshots_added_rows():
    a = Snapshot(name="a", table="users", rows=[{"id": 1}])
    b = Snapshot(name="b", table="users", rows=[{"id": 1}, {"id": 2}])
    diff = diff_snapshots(a, b)
    assert diff["added_count"] == 1
    assert diff["removed_count"] == 0


def test_diff_snapshots_removed_rows():
    a = Snapshot(name="a", table="users", rows=[{"id": 1}, {"id": 2}])
    b = Snapshot(name="b", table="users", rows=[{"id": 1}])
    diff = diff_snapshots(a, b)
    assert diff["removed_count"] == 1


def test_diff_snapshots_no_changes():
    a = Snapshot(name="a", table="users", rows=[{"id": 1}])
    b = Snapshot(name="b", table="users", rows=[{"id": 1}])
    diff = diff_snapshots(a, b)
    assert diff["added_count"] == 0
    assert diff["removed_count"] == 0
    assert diff["unchanged_count"] == 1


def test_diff_snapshots_keys():
    a = Snapshot(name="a", table="users", rows=[])
    b = Snapshot(name="b", table="users", rows=[])
    diff = diff_snapshots(a, b)
    assert "snapshot_a" in diff
    assert "snapshot_b" in diff
    assert "table" in diff
