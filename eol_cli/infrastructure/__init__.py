"""Infrastructure adapters for external services."""

from eol_cli.infrastructure.gateways import (
    EOLCategoryGatewayAdapter,
    EOLIdentifierGatewayAdapter,
    EOLIndexGatewayAdapter,
    EOLProductGatewayAdapter,
    EOLTagGatewayAdapter,
)

__all__ = [
    "EOLCategoryGatewayAdapter",
    "EOLIdentifierGatewayAdapter",
    "EOLIndexGatewayAdapter",
    "EOLProductGatewayAdapter",
    "EOLTagGatewayAdapter",
]
