"""Row encoder: serialise rows into various binary/text wire formats."""
from __future__ import annotations

import base64
import json
import pickle
from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal

Encoding = Literal["json", "base64_json", "pickle_b64"]

SUPPORTED_ENCODINGS: tuple[str, ...] = ("json", "base64_json", "pickle_b64")


class EncoderError(ValueError):
    """Raised when encoding fails or an unsupported encoding is requested."""


@dataclass
class EncoderConfig:
    encoding: Encoding = "json"
    indent: int | None = None
    ensure_ascii: bool = True

    def __post_init__(self) -> None:
        if self.encoding not in SUPPORTED_ENCODINGS:
            raise EncoderError(
                f"Unsupported encoding '{self.encoding}'. "
                f"Choose from: {', '.join(SUPPORTED_ENCODINGS)}"
            )
        if self.indent is not None and self.indent < 0:
            raise EncoderError("indent must be None or a non-negative integer.")


def _coerce_row(row: Dict[str, Any]) -> Dict[str, Any]:
    """Return a JSON-safe copy of *row*."""
    safe: Dict[str, Any] = {}
    for k, v in row.items():
        if isinstance(v, (str, int, float, bool, type(None))):
            safe[k] = v
        else:
            safe[k] = str(v)
    return safe


def encode_row(row: Dict[str, Any], config: EncoderConfig | None = None) -> str:
    """Encode a single *row* dict according to *config*."""
    cfg = config or EncoderConfig()
    safe = _coerce_row(row)

    if cfg.encoding == "json":
        return json.dumps(safe, indent=cfg.indent, ensure_ascii=cfg.ensure_ascii)

    if cfg.encoding == "base64_json":
        raw = json.dumps(safe, ensure_ascii=cfg.ensure_ascii).encode("utf-8")
        return base64.b64encode(raw).decode("ascii")

    if cfg.encoding == "pickle_b64":
        raw = pickle.dumps(safe)
        return base64.b64encode(raw).decode("ascii")

    raise EncoderError(f"Unhandled encoding: {cfg.encoding}")


def encode_rows(
    rows: List[Dict[str, Any]], config: EncoderConfig | None = None
) -> List[str]:
    """Encode each row in *rows* and return the list of encoded strings."""
    cfg = config or EncoderConfig()
    return [encode_row(r, cfg) for r in rows]


def decode_row(encoded: str, config: EncoderConfig | None = None) -> Dict[str, Any]:
    """Decode a single encoded string back to a row dict."""
    cfg = config or EncoderConfig()

    if cfg.encoding == "json":
        return json.loads(encoded)

    if cfg.encoding == "base64_json":
        raw = base64.b64decode(encoded.encode("ascii"))
        return json.loads(raw.decode("utf-8"))

    if cfg.encoding == "pickle_b64":
        raw = base64.b64decode(encoded.encode("ascii"))
        return pickle.loads(raw)  # noqa: S301

    raise EncoderError(f"Unhandled encoding: {cfg.encoding}")
