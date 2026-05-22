"""Row snapshot: capture and compare named snapshots of generated row sets."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Snapshot:
    name: str
    rows: List[Dict[str, Any]]
    table: str

    def __len__(self) -> int:
        return len(self.rows)

    def __repr__(self) -> str:  # pragma: no cover
        return f"Snapshot(name={self.name!r}, table={self.table!r}, rows={len(self.rows)})"


@dataclass
class SnapshotStore:
    _store: Dict[str, Snapshot] = field(default_factory=dict)

    def save(self, name: str, table: str, rows: List[Dict[str, Any]]) -> Snapshot:
        """Save a named snapshot of rows for a table."""
        if not name:
            raise ValueError("Snapshot name must not be empty.")
        snap = Snapshot(name=name, table=table, rows=[dict(r) for r in rows])
        self._store[name] = snap
        return snap

    def load(self, name: str) -> Optional[Snapshot]:
        """Return the snapshot with the given name, or None if not found."""
        return self._store.get(name)

    def delete(self, name: str) -> None:
        """Remove a snapshot by name. No-op if not found."""
        self._store.pop(name, None)

    def names(self) -> List[str]:
        """Return all stored snapshot names."""
        return list(self._store.keys())

    def clear(self) -> None:
        """Remove all snapshots."""
        self._store.clear()


def diff_snapshots(
    a: Snapshot, b: Snapshot
) -> Dict[str, Any]:
    """Return a summary dict describing differences between two snapshots."""
    added = [r for r in b.rows if r not in a.rows]
    removed = [r for r in a.rows if r not in b.rows]
    return {
        "snapshot_a": a.name,
        "snapshot_b": b.name,
        "table": a.table,
        "added": added,
        "removed": removed,
        "added_count": len(added),
        "removed_count": len(removed),
        "unchanged_count": len(a.rows) - len(removed),
    }
