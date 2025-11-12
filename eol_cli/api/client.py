"""API client for endoflife.date API v1.2.0."""

from typing import Any

import requests
from requests.exceptions import HTTPError, RequestException


class EOLAPIError(Exception):
    """Base exception for EOL API errors."""

    pass


class EOLNotFoundError(EOLAPIError):
    """Exception raised when a resource is not found."""

    pass


class EOLRateLimitError(EOLAPIError):
    """Exception raised when rate limit is exceeded."""

    pass


class EOLClient:
    """Client for interacting with the endoflife.date API.

    API Documentation: https://endoflife.date/docs/api/
    Base URL: https://endoflife.date/api/v1
    """

    BASE_URL = "https://endoflife.date/api/v1"

    def __init__(self, base_url: str | None = None, timeout: int = 30):
        """Initialize the EOL API client.

        Args:
            base_url: Optional custom base URL for the API
            timeout: Request timeout in seconds (default: 30)
        """
        self.base_url = base_url or self.BASE_URL
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "eol-cli/0.1.0 (https://github.com/seifreed/eol-cli)",
                "Accept": "application/json",
            }
        )

    def _request(self, endpoint: str) -> dict[str, Any]:
        """Make a request to the API.

        Args:
            endpoint: API endpoint path

        Returns:
            JSON response as dictionary

        Raises:
            EOLNotFoundError: If the resource is not found (404)
            EOLRateLimitError: If rate limit is exceeded (429)
            EOLAPIError: For other API errors
        """
        url = f"{self.base_url}{endpoint}"

        try:
            response = self.session.get(url, timeout=self.timeout)

            # Handle specific status codes
            if response.status_code == 404:
                raise EOLNotFoundError(f"Resource not found: {endpoint}")
            elif response.status_code == 429:
                retry_after = response.headers.get("Retry-After", "unknown")
                raise EOLRateLimitError(f"Rate limit exceeded. Retry after: {retry_after} seconds")

            # Raise for other HTTP errors
            response.raise_for_status()

            return response.json()

        except HTTPError as e:
            raise EOLAPIError(f"HTTP error occurred: {e}") from e
        except RequestException as e:
            raise EOLAPIError(f"Request failed: {e}") from e
        except ValueError as e:
            raise EOLAPIError(f"Invalid JSON response: {e}") from e

    # Index endpoint
    def get_index(self) -> dict[str, Any]:
        """Get the API index with main endpoints.

        Returns:
            Dictionary with schema_version, total, and result (list of URIs)
        """
        return self._request("/")

    # Products endpoints
    def list_products(self) -> dict[str, Any]:
        """List all products (summary).

        Returns:
            Dictionary with schema_version, total, and result (list of product summaries)
        """
        return self._request("/products")

    def list_products_full(self) -> dict[str, Any]:
        """List all products with full details.

        Returns:
            Dictionary with schema_version, total, and result (list of full product details)
        """
        return self._request("/products/full")

    def get_product(self, product: str) -> dict[str, Any]:
        """Get details for a specific product.

        Args:
            product: Product name (e.g., 'ubuntu', 'python')

        Returns:
            Dictionary with schema_version, last_modified, and result (product details)
        """
        return self._request(f"/products/{product}")

    def get_product_release(self, product: str, release: str) -> dict[str, Any]:
        """Get information about a specific product release cycle.

        Args:
            product: Product name
            release: Release cycle name

        Returns:
            Dictionary with schema_version and result (release information)
        """
        return self._request(f"/products/{product}/releases/{release}")

    def get_product_latest_release(self, product: str) -> dict[str, Any]:
        """Get the latest release cycle for a product.

        Args:
            product: Product name

        Returns:
            Dictionary with schema_version and result (latest release information)
        """
        return self._request(f"/products/{product}/releases/latest")

    # Categories endpoints
    def list_categories(self) -> dict[str, Any]:
        """List all categories.

        Returns:
            Dictionary with schema_version, total, and result (list of category URIs)
        """
        return self._request("/categories")

    def get_category_products(self, category: str) -> dict[str, Any]:
        """Get all products in a specific category.

        Args:
            category: Category name (e.g., 'os', 'app', 'framework')

        Returns:
            Dictionary with schema_version, total, and result (list of products)
        """
        return self._request(f"/categories/{category}")

    # Tags endpoints
    def list_tags(self) -> dict[str, Any]:
        """List all tags.

        Returns:
            Dictionary with schema_version, total, and result (list of tag URIs)
        """
        return self._request("/tags")

    def get_tag_products(self, tag: str) -> dict[str, Any]:
        """Get all products with a specific tag.

        Args:
            tag: Tag name (e.g., 'linux', 'database')

        Returns:
            Dictionary with schema_version, total, and result (list of products)
        """
        return self._request(f"/tags/{tag}")

    # Identifiers endpoints
    def list_identifier_types(self) -> dict[str, Any]:
        """List all identifier types (purl, cpe, etc.).

        Returns:
            Dictionary with schema_version, total, and result (list of identifier type URIs)
        """
        return self._request("/identifiers")

    def get_identifiers_by_type(self, identifier_type: str) -> dict[str, Any]:
        """Get all identifiers for a specific type.

        Args:
            identifier_type: Identifier type (e.g., 'purl', 'cpe', 'repology')

        Returns:
            Dictionary with schema_version, total, and result (list of identifiers with products)
        """
        return self._request(f"/identifiers/{identifier_type}")

    def close(self):
        """Close the HTTP session."""
        self.session.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
