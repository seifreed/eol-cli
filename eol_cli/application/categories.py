"""Application use cases for category-related operations."""

from dataclasses import dataclass

from eol_cli.domain.contracts import ResponseEnvelope
from eol_cli.domain.ports import CategoryGateway


@dataclass(frozen=True)
class ListCategoriesCommand:
    """Fetch all categories."""

    category_gateway: CategoryGateway

    def run(self) -> ResponseEnvelope:
        """Return all category resources."""
        return self.category_gateway.list_categories()


@dataclass(frozen=True)
class GetCategoryProductsCommand:
    """Fetch all products for a specific category."""

    category_gateway: CategoryGateway

    def run(self, category: str) -> ResponseEnvelope:
        """Return products for a category."""
        return self.category_gateway.get_category_products(category)
