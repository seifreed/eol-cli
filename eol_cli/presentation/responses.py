"""Presentation-layer response DTOs and serialization helpers."""

from __future__ import annotations

from collections.abc import Iterator, Mapping, Sequence
from dataclasses import dataclass, field, replace

from eol_cli.domain.contracts import DEFAULT_API_SCHEMA_VERSION, ResponseEnvelope


def _schema_version_key(version: object) -> tuple[int, tuple[int, ...], str]:
    """Sort schema versions numerically when possible."""
    if not isinstance(version, str) or not version.strip():
        return (0, (), "")

    version_parts = version.split(".")
    numeric_parts: list[int] = []
    for part in version_parts:
        if part.isdigit():
            numeric_parts.append(int(part))
        else:
            return (0, (), version)

    return (1, tuple(numeric_parts), version)


def _normalize_schema_version(version: object) -> str:
    if not isinstance(version, str) or not version.strip():
        return DEFAULT_API_SCHEMA_VERSION
    return version


def _payload_from_envelope(
    envelope: ResponseEnvelope, *, result_key: str = "result"
) -> dict[str, object]:
    payload: dict[str, object] = {
        "schema_version": _normalize_schema_version(envelope.schema_version),
        result_key: envelope.result,
    }
    if envelope.total is not None:
        payload["total"] = envelope.total
    if envelope.last_modified is not None:
        payload["last_modified"] = envelope.last_modified
    if envelope.meta:
        payload["meta"] = dict(envelope.meta)
    return payload


@dataclass(frozen=True)
class ApiResponse(Mapping[str, object]):
    """Typed presentation response with mapping behavior for compatibility."""

    schema_version: str = DEFAULT_API_SCHEMA_VERSION
    result: object = field(default_factory=dict)
    total: int | None = None
    last_modified: str | None = None
    meta: Mapping[str, object] = field(default_factory=dict)
    result_key: str = "result"
    _payload: dict[str, object] = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "_payload", self._build_payload())

    def _build_payload(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "schema_version": _normalize_schema_version(self.schema_version),
            self.result_key: self.result,
        }
        if self.total is not None:
            payload["total"] = self.total
        if self.last_modified is not None:
            payload["last_modified"] = self.last_modified
        if self.meta:
            payload["meta"] = dict(self.meta)
        return payload

    @classmethod
    def from_payload(
        cls, payload: Mapping[str, object], *, result_key: str = "result"
    ) -> ApiResponse:
        """Create an ``ApiResponse`` from a raw payload mapping."""
        schema_version = _normalize_schema_version(payload.get("schema_version"))

        result = payload.get(result_key, payload.get("result"))
        total = payload.get("total")
        last_modified = payload.get("last_modified")
        meta = payload.get("meta", {})
        if not isinstance(meta, Mapping):
            meta = {}

        return cls(
            schema_version=schema_version,
            result=result,
            total=total if isinstance(total, int) else None,
            last_modified=last_modified if isinstance(last_modified, str) else None,
            meta=dict(meta),
            result_key=result_key,
        )

    @classmethod
    def from_envelope(
        cls, envelope: ResponseEnvelope, *, result_key: str = "result"
    ) -> ApiResponse:
        """Create an ``ApiResponse`` from a domain response envelope."""
        return cls(
            schema_version=_normalize_schema_version(envelope.schema_version),
            result=envelope.result,
            total=envelope.total,
            last_modified=envelope.last_modified,
            meta=dict(envelope.meta),
            result_key=result_key,
        )

    def to_payload(self) -> dict[str, object]:
        """Return a plain dictionary payload suitable for formatters."""
        return dict(self._payload)

    def with_meta(self, **entries: object) -> ApiResponse:
        """Return a copy with metadata merged into the payload."""
        meta = dict(self.meta)
        meta.update(entries)
        return replace(self, meta=meta)

    def __getitem__(self, key: str) -> object:
        return self._payload[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self._payload)

    def __len__(self) -> int:
        return len(self._payload)


def response_payload(document: ResponseEnvelope | ApiResponse) -> dict[str, object]:
    """Serialize a response envelope or presentation response into a payload."""
    if isinstance(document, ResponseEnvelope):
        return _payload_from_envelope(document)

    payload = document.to_payload()
    if not isinstance(payload, dict):
        raise TypeError("Presentation responses must serialize to a dictionary payload")
    return payload


def response_payloads(documents: Sequence[ResponseEnvelope]) -> list[dict[str, object]]:
    """Serialize a sequence of response envelopes into plain dictionary payloads."""
    return [_payload_from_envelope(document) for document in documents]


def create_aggregated_response(all_data: Sequence[ResponseEnvelope]) -> ApiResponse:
    """Create a multi-product aggregation payload."""
    if not all_data:
        raise ValueError("Cannot create aggregated response from empty list")

    payloads = response_payloads(all_data)
    schema_version = max((item.schema_version for item in all_data), key=_schema_version_key)
    schema_version = _normalize_schema_version(schema_version)

    return ApiResponse(
        schema_version=schema_version,
        total=len(payloads),
        result=payloads,
        result_key="products",
    )
