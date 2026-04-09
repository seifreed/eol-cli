"""Domain-level exception hierarchy for EOL operations."""


class DomainError(Exception):
    """Base exception for domain failures."""


class ProductLookupError(DomainError):
    """Raised when a product lookup operation cannot be performed."""


class SuggestionServiceError(DomainError):
    """Raised when suggestions cannot be loaded from the catalog."""


class GatewayError(DomainError):
    """Raised when a gateway operation fails unexpectedly."""


class NotFoundError(GatewayError):
    """Raised when a requested resource is not found."""


class RateLimitError(GatewayError):
    """Raised when a gateway request is rate limited."""


class OutputSelectionError(DomainError):
    """Raised when output mode selection is invalid."""
