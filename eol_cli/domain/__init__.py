"""Domain layer for EOL CLI."""

from eol_cli.domain.contracts import ResponseEnvelope
from eol_cli.domain.errors import (
    DomainError,
    GatewayError,
    NotFoundError,
    OutputSelectionError,
    ProductLookupError,
    RateLimitError,
    SuggestionServiceError,
)
from eol_cli.domain.models import FetchSummary, ProductLookupResult, merge_not_found
from eol_cli.domain.output import (
    OutputFormatCommand,
    OutputMode,
    OutputRenderResult,
    RenderOutputCommand,
    resolve_output_mode,
)
from eol_cli.domain.ports import (
    CategoryGateway,
    IdentifierGateway,
    IndexGateway,
    ProductCatalogGateway,
    ProductGateway,
    ProductReleaseGateway,
    TagGateway,
)

__all__ = [
    "DomainError",
    "GatewayError",
    "NotFoundError",
    "RateLimitError",
    "OutputSelectionError",
    "ProductLookupError",
    "SuggestionServiceError",
    "FetchSummary",
    "ProductLookupResult",
    "merge_not_found",
    "ResponseEnvelope",
    "OutputFormatCommand",
    "OutputMode",
    "OutputRenderResult",
    "RenderOutputCommand",
    "resolve_output_mode",
    "CategoryGateway",
    "IdentifierGateway",
    "IndexGateway",
    "ProductGateway",
    "ProductCatalogGateway",
    "ProductReleaseGateway",
    "TagGateway",
]
