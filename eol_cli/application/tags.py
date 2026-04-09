"""Application use cases for tag-related operations."""

from dataclasses import dataclass

from eol_cli.domain.contracts import ResponseEnvelope
from eol_cli.domain.ports import TagGateway


@dataclass(frozen=True)
class ListTagsCommand:
    """Fetch all tags."""

    tag_gateway: TagGateway

    def run(self) -> ResponseEnvelope:
        """Return all tag resources."""
        return self.tag_gateway.list_tags()


@dataclass(frozen=True)
class GetTagProductsCommand:
    """Fetch all products for a specific tag."""

    tag_gateway: TagGateway

    def run(self, tag: str) -> ResponseEnvelope:
        """Return products for a tag."""
        return self.tag_gateway.get_tag_products(tag)
