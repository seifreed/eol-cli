"""API client for endoflife.date API v1.2.0."""

import time
from typing import Any, NoReturn, cast
from urllib.parse import quote

import requests
from requests.exceptions import HTTPError, JSONDecodeError, RequestException

from eol_cli._version import __version__

API_SCHEMA_VERSION = "1.2.0"


class EOLAPIError(Exception):
    """Base exception for EOL API errors."""

    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


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
                "User-Agent": f"eol-cli/{__version__} (https://github.com/seifreed/eol-cli)",
                "Accept": "application/json",
            }
        )

    @staticmethod
    def _build_url(base_url: str, endpoint: str) -> str:
        """Build the final endpoint URL."""
        return f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}"

    def _dispatch_status(self, endpoint: str, response: requests.Response) -> None:
        """Translate HTTP statuses to domain-specific exceptions when needed."""
        if response.status_code == 404:
            raise EOLNotFoundError(f"Resource not found: {endpoint}")
        if response.status_code == 429:
            retry_after = response.headers.get("Retry-After", "unknown")
            raise EOLRateLimitError(f"Rate limit exceeded. Retry after: {retry_after}")
        response.raise_for_status()

    @staticmethod
    def _extract_status_code(error: Exception) -> int | None:
        """Read status code from known error shapes."""
        if isinstance(error, EOLAPIError):
            return error.status_code
        response = getattr(error, "response", None)
        if response is not None:
            status_code = getattr(response, "status_code", None)
            if isinstance(status_code, int):
                return status_code
        return None

    def _should_retry(self, error: Exception, attempt: int, max_retries: int) -> bool:
        """Return True when an error is transient and retries remain."""
        if attempt >= max_retries:
            return False
        if isinstance(error, RequestException):
            return not isinstance(error, HTTPError)
        if not isinstance(error, HTTPError):
            return False
        status_code = self._extract_status_code(error)
        return status_code is not None and status_code >= 500

    @staticmethod
    def _should_retry_delay(attempt: int) -> float:
        """Compute exponential backoff delay for a retry attempt."""
        return float(2**attempt)

    @staticmethod
    def _parse_json(response: requests.Response) -> dict[str, Any]:
        """Parse response body as JSON."""
        payload = response.json()
        if not isinstance(payload, dict):
            raise EOLAPIError("Invalid JSON response from API: expected an object")
        return cast(dict[str, Any], payload)

    def _raise_final_error(
        self, endpoint: str, max_retries: int, last_error: Exception | None
    ) -> NoReturn:
        """Raise a final aggregated API error after retries are exhausted."""
        status_code = self._extract_status_code(last_error) if last_error else None
        raise EOLAPIError(
            (
                f"Request failed after {max_retries} retries ({max_retries + 1} attempts): "
                f"{last_error}"
            ),
            status_code=status_code,
        )

    def _request(self, endpoint: str, max_retries: int = 3) -> dict[str, Any]:
        """Make a request to the API with retry logic for transient failures.

        Args:
            endpoint: API endpoint path
            max_retries: Maximum number of retry attempts (default: 3)

        Returns:
            JSON response as dictionary

        Raises:
            EOLNotFoundError: If the resource is not found (404)
            EOLRateLimitError: If rate limit is exceeded (429)
            EOLAPIError: For other API errors
        """
        url = self._build_url(self.base_url, endpoint)
        last_error: Exception | None = None

        for attempt in range(max_retries + 1):  # 1 initial + max_retries retries
            try:
                response = self.session.get(url, timeout=self.timeout)
                self._dispatch_status(endpoint, response)
                return self._parse_json(response)
            except HTTPError as e:
                last_error = e
                status_code = self._extract_status_code(e)
                if status_code is not None and 400 <= status_code < 500:
                    raise EOLAPIError(f"HTTP error occurred: {e}", status_code=status_code) from e
                if self._should_retry(e, attempt, max_retries):
                    time.sleep(self._should_retry_delay(attempt))
                    continue
            except RequestException as e:
                last_error = e
                if self._should_retry(e, attempt, max_retries):
                    time.sleep(self._should_retry_delay(attempt))
                    continue
            except (JSONDecodeError, ValueError) as e:
                raise EOLAPIError(f"Invalid JSON response from API: {e}") from e

        # All retries exhausted for transient errors (5xx, network)
        self._raise_final_error(endpoint, max_retries, last_error)

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
        return self._request(f"/products/{quote(product, safe='')}")

    def get_product_release(self, product: str, release: str) -> dict[str, Any]:
        """Get information about a specific product release cycle.

        Args:
            product: Product name
            release: Release cycle name

        Returns:
            Dictionary with schema_version and result (release information)
        """
        return self._request(
            f"/products/{quote(product, safe='')}/releases/{quote(release, safe='')}"
        )

    def get_product_latest_release(self, product: str) -> dict[str, Any]:
        """Get the latest release cycle for a product.

        Args:
            product: Product name

        Returns:
            Dictionary with schema_version and result (latest release information)
        """
        return self._request(f"/products/{quote(product, safe='')}/releases/latest")

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
        return self._request(f"/categories/{quote(category, safe='')}")

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
        return self._request(f"/tags/{quote(tag, safe='')}")

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
        return self._request(f"/identifiers/{quote(identifier_type, safe='')}")

    def close(self) -> None:
        """Close the HTTP session."""
        self.session.close()

    def __enter__(self) -> "EOLClient":
        """Context manager entry."""
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object,
    ) -> None:
        """Context manager exit; does not suppress exceptions."""
        self.close()
