"""Row projector: select or exclude specific columns from generated rows."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Set


class ProjectorError(Exception):
    """Raised when the projector configuration is invalid."""


@dataclass
class ProjectorConfig:
    """Configuration for column projection.

    Either *include* or *exclude* may be set, but not both.
    """

    include: Optional[List[str]] = None
    exclude: Optional[List[str]] = None
    case_sensitive: bool = False

    def __post_init__(self) -> None:
        if self.include is not None and self.exclude is not None:
            raise ProjectorError("Cannot specify both 'include' and 'exclude'.")
        if self.include is not None:
            self.include = self._normalise(self.include)
        if self.exclude is not None:
            self.exclude = self._normalise(self.exclude)

    def _normalise(self, columns: List[str]) -> List[str]:
        if not self.case_sensitive:
            return [c.lower() for c in columns]
        return list(columns)

    def _key(self, name: str) -> str:
        return name if self.case_sensitive else name.lower()

    def project(self, row: Dict) -> Dict:
        """Return a new row containing only the projected columns."""
        if self.include is not None:
            allowed: Set[str] = set(self.include)
            return {k: v for k, v in row.items() if self._key(k) in allowed}
        if self.exclude is not None:
            blocked: Set[str] = set(self.exclude)
            return {k: v for k, v in row.items() if self._key(k) not in blocked}
        return dict(row)


def project_rows(
    rows: Iterable[Dict],
    config: ProjectorConfig,
) -> List[Dict]:
    """Apply *config* projection to every row in *rows*."""
    return [config.project(row) for row in rows]


def project_columns(
    rows: Iterable[Dict],
    include: Optional[List[str]] = None,
    exclude: Optional[List[str]] = None,
    case_sensitive: bool = False,
) -> List[Dict]:
    """Convenience wrapper that builds a :class:`ProjectorConfig` and projects."""
    cfg = ProjectorConfig(
        include=include,
        exclude=exclude,
        case_sensitive=case_sensitive,
    )
    return project_rows(rows, cfg)
