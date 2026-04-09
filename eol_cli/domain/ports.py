"""Interface contracts used by application services."""

from typing import Protocol, runtime_checkable

from eol_cli.domain.contracts import ResponseEnvelope


@runtime_checkable
class ProductGateway(Protocol):
    """Protocol for product and index queries."""

    def list_products(self) -> ResponseEnvelope: ...

    def get_product(self, product: str) -> ResponseEnvelope: ...


@runtime_checkable
class ProductCatalogGateway(Protocol):
    """Protocol for complete catalog/product listing queries."""

    def list_products(self) -> ResponseEnvelope: ...

    def list_products_full(self) -> ResponseEnvelope: ...


@runtime_checkable
class ProductReleaseGateway(Protocol):
    """Protocol for product release detail queries."""

    def get_product_release(self, product: str, release: str) -> ResponseEnvelope: ...

    def get_product_latest_release(self, product: str) -> ResponseEnvelope: ...


@runtime_checkable
class CategoryGateway(Protocol):
    """Protocol for retrieving output-oriented resources."""

    def get_category_products(self, category: str) -> ResponseEnvelope: ...

    def list_categories(self) -> ResponseEnvelope: ...


@runtime_checkable
class IndexGateway(Protocol):
    """Protocol for index resources."""

    def get_index(self) -> ResponseEnvelope: ...


@runtime_checkable
class TagGateway(Protocol):
    """Protocol for tag-related queries."""

    def list_tags(self) -> ResponseEnvelope: ...

    def get_tag_products(self, tag: str) -> ResponseEnvelope: ...


@runtime_checkable
class IdentifierGateway(Protocol):
    """Protocol for identifier-related queries."""

    def list_identifier_types(self) -> ResponseEnvelope: ...

    def get_identifiers_by_type(self, identifier_type: str) -> ResponseEnvelope: ...
