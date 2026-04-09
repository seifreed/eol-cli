"""Application use cases for product-related operations."""

from __future__ import annotations

from dataclasses import dataclass

from eol_cli.domain import (
    FetchSummary,
    GatewayError,
    NotFoundError,
    ProductLookupError,
    ProductLookupResult,
    RateLimitError,
    merge_not_found,
)
from eol_cli.domain.contracts import ResponseEnvelope
from eol_cli.domain.ports import ProductCatalogGateway, ProductGateway, ProductReleaseGateway
from eol_cli.utils.fuzzy_search import find_similar_products


def parse_product_names(product_names: str) -> list[str]:
    """Normalize and deduplicate comma-separated product names."""
    normalized = [name.strip() for name in product_names.split(",") if name.strip()]
    return list(dict.fromkeys(normalized))


def _deduplicate_names(names: list[str]) -> list[str]:
    """Preserve order while removing duplicates."""
    return list(dict.fromkeys(names))


def _extract_product_names(all_products_data: ResponseEnvelope) -> list[str]:
    result = all_products_data.result
    if not isinstance(result, list):
        return []

    names: list[str] = []
    for item in result:
        if isinstance(item, dict):
            name = item.get("name")
            if isinstance(name, str) and name.strip():
                names.append(name.strip())
    return names


def _suggestions_for_not_found_products(
    product_gateway: ProductGateway, missing_products: list[str]
) -> tuple[dict[str, list[tuple[str, float]]], list[str]]:
    if not missing_products:
        return {}, []

    warnings: list[str] = []
    not_found_sorted = sorted(set(missing_products))
    try:
        all_products_data = product_gateway.list_products()
    except RateLimitError as exc:
        warnings.append(f"(Rate limited, cannot fetch suggestions: {exc})")
        return {}, warnings
    except GatewayError as exc:
        if isinstance(exc, NotFoundError):
            return {}, warnings
        warnings.append(f"(Could not fetch suggestions: {exc})")
        return {}, warnings

    all_product_names = _extract_product_names(all_products_data)
    if not all_product_names:
        return {}, warnings

    suggestions = {
        product: find_similar_products(product, all_product_names) for product in not_found_sorted
    }
    return suggestions, warnings


@dataclass(frozen=True)
class ProductLookupCommand:
    """Orchestrate a list of product lookup operations."""

    product_gateway: ProductGateway

    def run(self, raw_product_names: list[str]) -> ProductLookupResult:
        normalized = _deduplicate_names(raw_product_names)
        products: list[ResponseEnvelope] = []
        errors: list[str] = []
        not_found: list[str] = []

        for product in normalized:
            try:
                products.append(self.product_gateway.get_product(product))
            except NotFoundError:
                errors.append(f"Product '{product}' not found")
                not_found.append(product)
            except GatewayError as exc:
                errors.append(f"Error fetching '{product}': {exc}")

        summary = FetchSummary(
            requested=len(normalized),
            succeeded=len(products),
            failed=len(errors),
            errors=errors,
            not_found=merge_not_found(not_found),
        )
        suggestions, warnings = _suggestions_for_not_found_products(self.product_gateway, not_found)

        return ProductLookupResult(
            products=products,
            summary=summary,
            suggestions_by_product=suggestions,
            warnings=warnings,
        )


@dataclass(frozen=True)
class ProductGetOutput:
    """Output shape used by product query commands."""

    lookup_result: ProductLookupResult


@dataclass(frozen=True)
class GetProductsCommand:
    """Orchestrate retrieval of one or more products with lookup metadata."""

    product_gateway: ProductGateway

    def run(self, product_names: str) -> ProductGetOutput:
        """Run product lookup and return command-oriented output state."""
        parsed = parse_product_names(product_names)
        if not parsed:
            raise ProductLookupError("No valid product names provided")

        lookup_result = ProductLookupCommand(product_gateway=self.product_gateway).run(parsed)
        return ProductGetOutput(lookup_result=lookup_result)


@dataclass(frozen=True)
class ListProductsCommand:
    """List products, optionally returning full release information."""

    product_catalog_gateway: ProductCatalogGateway

    def run(self, full: bool = False) -> ResponseEnvelope:
        """Return products list in summary or full mode."""
        if full:
            return self.product_catalog_gateway.list_products_full()

        return self.product_catalog_gateway.list_products()


@dataclass(frozen=True)
class GetProductReleaseCommand:
    """Get a product-specific release payload from the API."""

    product_release_gateway: ProductReleaseGateway

    def run(self, product: str, release: str) -> ResponseEnvelope:
        """Return the latest release when `release` is latest, otherwise by name."""
        if release.lower() == "latest":
            return self.product_release_gateway.get_product_latest_release(product)

        return self.product_release_gateway.get_product_release(product, release)
