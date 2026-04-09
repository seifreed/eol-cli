"""Domain models for product lookup workflows."""

from collections.abc import Iterable
from dataclasses import dataclass, field

from eol_cli.domain.contracts import ResponseEnvelope


@dataclass(frozen=True)
class FetchSummary:
    """Summary information for a fetch operation."""

    requested: int
    succeeded: int
    failed: int
    errors: list[str]
    not_found: list[str]

    @property
    def has_failures(self) -> bool:
        return self.failed > 0

    @property
    def has_rejected(self) -> bool:
        return self.failed >= self.requested

    @property
    def has_success(self) -> bool:
        return self.succeeded > 0


@dataclass(frozen=True)
class ProductLookupResult:
    """Result of a multi-product lookup."""

    products: list[ResponseEnvelope]
    summary: FetchSummary
    suggestions_by_product: dict[str, list[tuple[str, float]]]
    warnings: list[str] = field(default_factory=list)

    @property
    def has_products(self) -> bool:
        return bool(self.products)

    @property
    def has_partial(self) -> bool:
        return self.summary.has_failures and self.summary.has_success

    @property
    def has_rejected(self) -> bool:
        return self.summary.failed >= self.summary.requested

    def as_fetch_summary(self) -> dict[str, object]:
        """Convert summary data to a presentation-friendly payload."""
        return {
            "requested": self.summary.requested,
            "succeeded": self.summary.succeeded,
            "failed": self.summary.failed,
            "errors": self.summary.errors,
            "not_found": self.summary.not_found,
        }


def merge_not_found(values: Iterable[str]) -> list[str]:
    """Sort and deduplicate not-found items deterministically."""
    return sorted(set(values))
