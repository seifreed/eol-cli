"""API client module for endoflife.date API."""

from eol_cli.api.client import (
    API_SCHEMA_VERSION,
    EOLAPIError,
    EOLClient,
    EOLNotFoundError,
    EOLRateLimitError,
)

__all__ = [
    "API_SCHEMA_VERSION",
    "EOLAPIError",
    "EOLClient",
    "EOLNotFoundError",
    "EOLRateLimitError",
]
