"""Application use cases for identifier-related operations."""

from dataclasses import dataclass

from eol_cli.domain.contracts import ResponseEnvelope
from eol_cli.domain.ports import IdentifierGateway


@dataclass(frozen=True)
class ListIdentifierTypesCommand:
    """Fetch available identifier types."""

    identifier_gateway: IdentifierGateway

    def run(self) -> ResponseEnvelope:
        """Return available identifier types."""
        return self.identifier_gateway.list_identifier_types()


@dataclass(frozen=True)
class GetIdentifiersByTypeCommand:
    """Fetch identifiers for a specific type."""

    identifier_gateway: IdentifierGateway

    def run(self, identifier_type: str) -> ResponseEnvelope:
        """Return all identifiers for a type."""
        return self.identifier_gateway.get_identifiers_by_type(identifier_type)
