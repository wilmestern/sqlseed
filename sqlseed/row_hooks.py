"""Row lifecycle hooks for pre/post row generation events."""
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

RowDict = Dict[str, object]
HookFn = Callable[[str, RowDict], Optional[RowDict]]


@dataclass
class RowHooks:
    """Registry of before/after hooks keyed by hook name."""
    _before: Dict[str, HookFn] = field(default_factory=dict)
    _after: Dict[str, HookFn] = field(default_factory=dict)

    def before(self, name: str, fn: HookFn) -> None:
        """Register a hook to run before a row is generated."""
        if not callable(fn):
            raise TypeError(f"Hook '{name}' must be callable")
        self._before[name] = fn

    def after(self, name: str, fn: HookFn) -> None:
        """Register a hook to run after a row is generated."""
        if not callable(fn):
            raise TypeError(f"Hook '{name}' must be callable")
        self._after[name] = fn

    def remove_before(self, name: str) -> None:
        self._before.pop(name, None)

    def remove_after(self, name: str) -> None:
        self._after.pop(name, None)

    def clear(self) -> None:
        self._before.clear()
        self._after.clear()

    def before_names(self) -> List[str]:
        return list(self._before.keys())

    def after_names(self) -> List[str]:
        return list(self._after.keys())

    def run_before(self, table_name: str, row: RowDict) -> RowDict:
        """Run all before-hooks in registration order; each may mutate/replace row."""
        for fn in self._before.values():
            result = fn(table_name, row)
            if result is not None:
                row = result
        return row

    def run_after(self, table_name: str, row: RowDict) -> RowDict:
        """Run all after-hooks in registration order; each may mutate/replace row."""
        for fn in self._after.values():
            result = fn(table_name, row)
            if result is not None:
                row = result
        return row


_default_hooks: RowHooks = RowHooks()


def get_default_hooks() -> RowHooks:
    return _default_hooks
