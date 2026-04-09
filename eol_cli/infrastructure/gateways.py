"""Adapters that translate EOL client errors into domain gateway errors."""

from collections.abc import Callable
from typing import Any

from eol_cli.api.client import EOLAPIError, EOLClient, EOLNotFoundError
from eol_cli.domain import GatewayError, NotFoundError
from eol_cli.domain.contracts import DEFAULT_API_SCHEMA_VERSION, ResponseEnvelope
from eol_cli.domain.ports import (
    CategoryGateway,
    IdentifierGateway,
    IndexGateway,
    ProductCatalogGateway,
    ProductGateway,
    ProductReleaseGateway,
    TagGateway,
)


class _EOLGatewayAdapter:
    """Base adapter that normalizes API client failures into domain errors."""

    def __init__(self, client: EOLClient) -> None:
        self._client = client

    def _call(self, operation: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        try:
            return operation(*args, **kwargs)
        except EOLNotFoundError as exc:
            raise NotFoundError(str(exc)) from exc
        except EOLAPIError as exc:
            raise GatewayError(str(exc)) from exc

    @staticmethod
    def _response(payload: dict[str, object], *, result_key: str = "result") -> ResponseEnvelope:
        """Convert raw client payloads into domain response envelopes."""
        schema_version = payload.get("schema_version", DEFAULT_API_SCHEMA_VERSION)
        if not isinstance(schema_version, str) or not schema_version.strip():
            schema_version = DEFAULT_API_SCHEMA_VERSION

        result = payload.get(result_key, payload.get("result"))
        total = payload.get("total")
        last_modified = payload.get("last_modified")
        meta = payload.get("meta", {})
        if not isinstance(meta, dict):
            meta = {}

        return ResponseEnvelope(
            schema_version=schema_version,
            result=result,
            total=total if isinstance(total, int) else None,
            last_modified=last_modified if isinstance(last_modified, str) else None,
            meta=meta,
        )


class EOLProductGatewayAdapter(
    _EOLGatewayAdapter, ProductGateway, ProductCatalogGateway, ProductReleaseGateway
):
    """Expose ``EOLClient`` as the product-related gateway set."""

    def list_products(self) -> ResponseEnvelope:
        return self._response(self._call(self._client.list_products))

    def list_products_full(self) -> ResponseEnvelope:
        return self._response(self._call(self._client.list_products_full))

    def get_product(self, product: str) -> ResponseEnvelope:
        return self._response(self._call(self._client.get_product, product))

    def get_product_latest_release(self, product: str) -> ResponseEnvelope:
        return self._response(self._call(self._client.get_product_latest_release, product))

    def get_product_release(self, product: str, release: str) -> ResponseEnvelope:
        return self._response(self._call(self._client.get_product_release, product, release))


class EOLCategoryGatewayAdapter(_EOLGatewayAdapter, CategoryGateway):
    """Expose ``EOLClient`` as the category gateway."""

    def list_categories(self) -> ResponseEnvelope:
        return self._response(self._call(self._client.list_categories))

    def get_category_products(self, category: str) -> ResponseEnvelope:
        return self._response(self._call(self._client.get_category_products, category))


class EOLTagGatewayAdapter(_EOLGatewayAdapter, TagGateway):
    """Expose ``EOLClient`` as the tag gateway."""

    def list_tags(self) -> ResponseEnvelope:
        return self._response(self._call(self._client.list_tags))

    def get_tag_products(self, tag: str) -> ResponseEnvelope:
        return self._response(self._call(self._client.get_tag_products, tag))


class EOLIdentifierGatewayAdapter(_EOLGatewayAdapter, IdentifierGateway):
    """Expose ``EOLClient`` as the identifier gateway."""

    def list_identifier_types(self) -> ResponseEnvelope:
        return self._response(self._call(self._client.list_identifier_types))

    def get_identifiers_by_type(self, identifier_type: str) -> ResponseEnvelope:
        return self._response(self._call(self._client.get_identifiers_by_type, identifier_type))


class EOLIndexGatewayAdapter(_EOLGatewayAdapter, IndexGateway):
    """Expose ``EOLClient`` as the index gateway."""

    def get_index(self) -> ResponseEnvelope:
        return self._response(self._call(self._client.get_index))
