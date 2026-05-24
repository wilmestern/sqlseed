"""Row annotator: attach metadata annotations to generated rows."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional


class AnnotatorError(Exception):
    """Raised when annotation configuration or application fails."""


@dataclass
class AnnotatorConfig:
    """Configuration for row annotation."""

    prefix: str = "__"
    suffix: str = "__"
    overwrite: bool = False

    def __post_init__(self) -> None:
        if not self.prefix and not self.suffix:
            raise AnnotatorError("At least one of prefix or suffix must be non-empty.")

    def annotation_key(self, name: str) -> str:
        """Return the full annotation key for a given annotation name."""
        return f"{self.prefix}{name}{self.suffix}"


@dataclass
class RowAnnotator:
    """Attaches computed annotations to rows."""

    config: AnnotatorConfig = field(default_factory=AnnotatorConfig)
    _annotations: Dict[str, Callable[[Dict[str, Any]], Any]] = field(
        default_factory=dict, init=False, repr=False
    )

    def add(self, name: str, fn: Callable[[Dict[str, Any]], Any]) -> None:
        """Register an annotation function under *name*."""
        if not callable(fn):
            raise AnnotatorError(f"Annotation '{name}' must be callable.")
        if not name:
            raise AnnotatorError("Annotation name must not be empty.")
        self._annotations[name] = fn

    def remove(self, name: str) -> None:
        """Remove a registered annotation by name (no-op if missing)."""
        self._annotations.pop(name, None)

    def clear(self) -> None:
        """Remove all registered annotations."""
        self._annotations.clear()

    def names(self) -> List[str]:
        """Return names of all registered annotations."""
        return list(self._annotations.keys())

    def annotate(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """Return a copy of *row* with annotation keys attached."""
        result = dict(row)
        for name, fn in self._annotations.items():
            key = self.config.annotation_key(name)
            if key in result and not self.config.overwrite:
                raise AnnotatorError(
                    f"Annotation key '{key}' already exists in row and overwrite=False."
                )
            result[key] = fn(row)
        return result

    def annotate_rows(
        self, rows: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Annotate every row in *rows* and return the annotated list."""
        return [self.annotate(row) for row in rows]
