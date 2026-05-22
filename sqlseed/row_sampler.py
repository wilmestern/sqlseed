"""row_sampler.py — Sample a subset of generated rows using configurable strategies."""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Callable, List, Optional

from sqlseed.schema_parser import TableDefinition


class SamplingError(Exception):
    """Raised when row sampling cannot be completed."""


@dataclass
class SamplerConfig:
    """Configuration for row sampling behaviour."""

    strategy: str = "random"  # "random", "first", "last"
    seed: Optional[int] = None
    predicate: Optional[Callable[[dict], bool]] = None

    def __post_init__(self) -> None:
        valid = {"random", "first", "last"}
        if self.strategy not in valid:
            raise ValueError(
                f"Invalid sampling strategy '{self.strategy}'. Choose from: {valid}"
            )


def sample_rows(
    rows: List[dict],
    n: int,
    config: Optional[SamplerConfig] = None,
) -> List[dict]:
    """Return up to *n* rows from *rows* using the configured strategy.

    Args:
        rows: The full list of generated row dicts.
        n: Maximum number of rows to return.
        config: Sampling configuration.  Defaults to random sampling.

    Returns:
        A list of at most *n* row dicts.

    Raises:
        SamplingError: If *n* is negative.
    """
    if n < 0:
        raise SamplingError(f"Sample size must be non-negative, got {n}.")

    if config is None:
        config = SamplerConfig()

    candidates = rows
    if config.predicate is not None:
        candidates = [r for r in rows if config.predicate(r)]

    if config.strategy == "first":
        return candidates[:n]

    if config.strategy == "last":
        return candidates[-n:] if n else []

    # random
    rng = random.Random(config.seed)
    k = min(n, len(candidates))
    return rng.sample(candidates, k)


def sample_table(
    table: TableDefinition,
    rows: List[dict],
    n: int,
    config: Optional[SamplerConfig] = None,
) -> List[dict]:
    """Convenience wrapper that validates the table has rows before sampling."""
    if not rows:
        return []
    return sample_rows(rows, n, config)
