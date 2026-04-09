"""Domain response envelopes shared across application and infrastructure."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field, replace

DEFAULT_API_SCHEMA_VERSION = "1.2.0"


@dataclass(frozen=True, slots=True)
class ResponseEnvelope:
    """Pure domain data carrier for API responses."""

    schema_version: str = DEFAULT_API_SCHEMA_VERSION
    result: object = field(default_factory=dict)
    total: int | None = None
    last_modified: str | None = None
    meta: Mapping[str, object] = field(default_factory=dict)

    def with_meta(self, **entries: object) -> ResponseEnvelope:
        """Return a copy with metadata merged into the envelope."""
        meta = dict(self.meta)
        meta.update(entries)
        return replace(self, meta=meta)
