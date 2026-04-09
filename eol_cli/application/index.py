"""Application use case for the API index command."""

from dataclasses import dataclass

from eol_cli.domain.contracts import ResponseEnvelope
from eol_cli.domain.ports import IndexGateway


@dataclass(frozen=True)
class GetIndexCommand:
    """Fetch the API index."""

    index_gateway: IndexGateway

    def run(self) -> ResponseEnvelope:
        """Return the API index."""
        return self.index_gateway.get_index()
