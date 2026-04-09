"""Tests for the API client."""

from collections.abc import Mapping, Sequence

import pytest
import requests

from eol_cli.api.client import EOLAPIError, EOLClient, EOLNotFoundError

pytestmark = pytest.mark.api


def _assert_mapping_has_keys(mapping: Mapping[str, object], keys: Sequence[str]) -> None:
    missing = [key for key in keys if key not in mapping]
    if missing:
        raise AssertionError(f"Missing keys: {', '.join(missing)}")


def _assert_sequence_of_mappings(items: Sequence[Mapping[str, object]]) -> None:
    if not items:
        raise AssertionError


def _assert_product_list_payload(data: Mapping[str, object]) -> None:
    _assert_mapping_has_keys(data, ("schema_version", "total", "result"))
    result = data["result"]
    if not isinstance(result, list):
        raise AssertionError
    _assert_sequence_of_mappings(result)

    product = result[0]
    if not isinstance(product, dict):
        raise AssertionError
    _assert_mapping_has_keys(product, ("name", "label", "category", "tags"))
    if not isinstance(product["tags"], list):
        raise AssertionError


def _assert_product_detail_payload(data: Mapping[str, object]) -> None:
    _assert_mapping_has_keys(data, ("schema_version", "last_modified", "result"))
    result = data["result"]
    if not isinstance(result, dict):
        raise AssertionError
    _assert_mapping_has_keys(result, ("name", "releases", "label", "category", "tags"))
    if not isinstance(result["releases"], list):
        raise AssertionError


class TestEOLClient:
    """Test suite for EOLClient."""

    def test_client_initialization(self):
        """Test that the client initializes correctly."""
        client = EOLClient()
        if not (client.base_url == EOLClient.BASE_URL):
            raise AssertionError
        if not (client.timeout == 30):
            raise AssertionError
        client.close()

    def test_client_custom_base_url(self):
        """Test client with custom base URL."""
        custom_url = "https://example.com/api"
        client = EOLClient(base_url=custom_url)
        if not (client.base_url == custom_url):
            raise AssertionError
        client.close()

    def test_client_custom_timeout(self):
        """Test client with custom timeout."""
        client = EOLClient(timeout=60)
        if not (client.timeout == 60):
            raise AssertionError
        client.close()

    def test_client_context_manager(self):
        """Test client as context manager."""
        with EOLClient() as client:
            if not (client is not None):
                raise AssertionError
            if not (client.session is not None):
                raise AssertionError


class TestIndexEndpoint:
    """Test index endpoint."""

    def test_get_index_returns_valid_data(self):
        """Test that get_index returns valid data."""
        with EOLClient() as client:
            data = client.get_index()
            if "schema_version" not in data:
                raise AssertionError
            if "total" not in data:
                raise AssertionError
            if "result" not in data:
                raise AssertionError
            if not (isinstance(data["result"], list)):
                raise AssertionError
            if not (data["total"] > 0):
                raise AssertionError

            # Verify structure of URI items
            for item in data["result"]:
                if "name" not in item:
                    raise AssertionError
                if "uri" not in item:
                    raise AssertionError


class TestProductsEndpoints:
    """Test products endpoints with real API calls."""

    def test_list_products_returns_valid_data(self):
        """Test that list_products returns valid data."""
        with EOLClient() as client:
            data = client.list_products()
            _assert_product_list_payload(data)
            if not (data["total"] > 0):
                raise AssertionError

    def test_list_products_full_returns_complete_data(self):
        """Test that list_products_full returns complete product data."""
        with EOLClient() as client:
            data = client.list_products_full()
            if "schema_version" not in data:
                raise AssertionError
            if "total" not in data:
                raise AssertionError
            if "result" not in data:
                raise AssertionError
            if not (isinstance(data["result"], list)):
                raise AssertionError

            # Verify full product has releases
            product = data["result"][0]
            if "releases" not in product:
                raise AssertionError
            if not (isinstance(product["releases"], list)):
                raise AssertionError

    def test_get_product_python_returns_valid_data(self):
        """Test get_product for Python returns valid data."""
        with EOLClient() as client:
            data = client.get_product("python")
            _assert_product_detail_payload(data)

            result = data["result"]
            if not (result["name"] == "python"):
                raise AssertionError
            if not (len(result["releases"]) > 0):
                raise AssertionError

    def test_get_product_ubuntu_returns_valid_data(self):
        """Test get_product for Ubuntu returns valid data."""
        with EOLClient() as client:
            data = client.get_product("ubuntu")
            if not (data["result"]["name"] == "ubuntu"):
                raise AssertionError
            if not (len(data["result"]["releases"]) > 0):
                raise AssertionError

    def test_get_product_not_found_raises_exception(self):
        """Test that getting a non-existent product raises EOLNotFoundError."""
        with EOLClient() as client:
            with pytest.raises(EOLNotFoundError):
                client.get_product("this-product-does-not-exist-12345")

    def test_get_product_release_python_returns_valid_data(self):
        """Test get_product_release for Python 3.11."""
        with EOLClient() as client:
            data = client.get_product_release("python", "3.11")
            if "schema_version" not in data:
                raise AssertionError
            if "result" not in data:
                raise AssertionError

            result = data["result"]
            if not (result["name"] == "3.11"):
                raise AssertionError
            if "releaseDate" not in result:
                raise AssertionError
            if "isEol" not in result:
                raise AssertionError
            if "eolFrom" not in result:
                raise AssertionError
            if "latest" not in result:
                raise AssertionError

    def test_get_product_release_not_found_raises_exception(self):
        """Test that non-existent release raises EOLNotFoundError."""
        with EOLClient() as client:
            with pytest.raises(EOLNotFoundError):
                client.get_product_release("python", "99.99")

    def test_get_product_latest_release_python(self):
        """Test get_product_latest_release for Python."""
        with EOLClient() as client:
            data = client.get_product_latest_release("python")
            if "schema_version" not in data:
                raise AssertionError
            if "result" not in data:
                raise AssertionError

            result = data["result"]
            if "name" not in result:
                raise AssertionError
            if "releaseDate" not in result:
                raise AssertionError
            if "isEol" not in result:
                raise AssertionError

    def test_get_product_latest_release_not_found_raises_exception(self):
        """Test that latest release for non-existent product raises error."""
        with EOLClient() as client:
            with pytest.raises(EOLNotFoundError):
                client.get_product_latest_release("nonexistent-product-xyz")


class TestCategoriesEndpoints:
    """Test categories endpoints."""

    def test_list_categories_returns_valid_data(self):
        """Test that list_categories returns valid data."""
        with EOLClient() as client:
            data = client.list_categories()
            if "schema_version" not in data:
                raise AssertionError
            if "total" not in data:
                raise AssertionError
            if "result" not in data:
                raise AssertionError
            if not (isinstance(data["result"], list)):
                raise AssertionError
            if not (data["total"] > 0):
                raise AssertionError

            # Verify category has expected fields
            category = data["result"][0]
            if "name" not in category:
                raise AssertionError
            if "uri" not in category:
                raise AssertionError

    def test_get_category_products_os_returns_valid_data(self):
        """Test get_category_products for 'os' category."""
        with EOLClient() as client:
            data = client.get_category_products("os")
            if "schema_version" not in data:
                raise AssertionError
            if "total" not in data:
                raise AssertionError
            if "result" not in data:
                raise AssertionError
            if not (isinstance(data["result"], list)):
                raise AssertionError
            if not (data["total"] > 0):
                raise AssertionError

            # Verify all products are in 'os' category
            for product in data["result"]:
                if not (product["category"] == "os"):
                    raise AssertionError

    def test_get_category_products_not_found_raises_exception(self):
        """Test that non-existent category raises EOLNotFoundError."""
        with EOLClient() as client:
            with pytest.raises(EOLNotFoundError):
                client.get_category_products("nonexistent-category-xyz")


class TestTagsEndpoints:
    """Test tags endpoints."""

    def test_list_tags_returns_valid_data(self):
        """Test that list_tags returns valid data."""
        with EOLClient() as client:
            data = client.list_tags()
            if "schema_version" not in data:
                raise AssertionError
            if "total" not in data:
                raise AssertionError
            if "result" not in data:
                raise AssertionError
            if not (isinstance(data["result"], list)):
                raise AssertionError
            if not (data["total"] > 0):
                raise AssertionError

    def test_get_tag_products_linux_distribution_returns_valid_data(self):
        """Test get_tag_products for 'linux-distribution'."""
        with EOLClient() as client:
            data = client.get_tag_products("linux-distribution")
            if "schema_version" not in data:
                raise AssertionError
            if "total" not in data:
                raise AssertionError
            if "result" not in data:
                raise AssertionError
            if not (isinstance(data["result"], list)):
                raise AssertionError
            if not (data["total"] > 0):
                raise AssertionError

            # Verify all products have the tag
            for product in data["result"]:
                if "linux-distribution" not in product["tags"]:
                    raise AssertionError

    def test_get_tag_products_not_found_raises_exception(self):
        """Test that non-existent tag raises EOLNotFoundError."""
        with EOLClient() as client:
            with pytest.raises(EOLNotFoundError):
                client.get_tag_products("nonexistent-tag-xyz-123")


class TestIdentifiersEndpoints:
    """Test identifiers endpoints."""

    def test_list_identifier_types_returns_valid_data(self):
        """Test that list_identifier_types returns valid data."""
        with EOLClient() as client:
            data = client.list_identifier_types()
            if "schema_version" not in data:
                raise AssertionError
            if "total" not in data:
                raise AssertionError
            if "result" not in data:
                raise AssertionError
            if not (isinstance(data["result"], list)):
                raise AssertionError
            if not (data["total"] > 0):
                raise AssertionError

    def test_get_identifiers_by_type_purl_returns_valid_data(self):
        """Test get_identifiers_by_type for 'purl'."""
        with EOLClient() as client:
            data = client.get_identifiers_by_type("purl")
            if "schema_version" not in data:
                raise AssertionError
            if "total" not in data:
                raise AssertionError
            if "result" not in data:
                raise AssertionError
            if not (isinstance(data["result"], list)):
                raise AssertionError
            if not (data["total"] > 0):
                raise AssertionError

            # Verify identifier structure
            identifier_entry = data["result"][0]
            if "identifier" not in identifier_entry:
                raise AssertionError
            if "product" not in identifier_entry:
                raise AssertionError
            if "name" not in identifier_entry["product"]:
                raise AssertionError
            if "uri" not in identifier_entry["product"]:
                raise AssertionError

    def test_get_identifiers_by_type_cpe_returns_valid_data(self):
        """Test get_identifiers_by_type for 'cpe'."""
        with EOLClient() as client:
            data = client.get_identifiers_by_type("cpe")
            if "total" not in data:
                raise AssertionError
            if not (data["total"] > 0):
                raise AssertionError

    def test_get_identifiers_by_type_not_found_raises_exception(self):
        """Test that non-existent identifier type raises EOLNotFoundError."""
        with EOLClient() as client:
            with pytest.raises(EOLNotFoundError):
                client.get_identifiers_by_type("nonexistent-type-xyz")


class TestErrorHandling:
    """Test error handling scenarios."""

    def test_invalid_base_url_raises_error(self):
        """Test that invalid base URL causes error."""
        client = EOLClient(base_url="https://invalid-url-that-does-not-exist.example.com")
        with pytest.raises(EOLAPIError):
            client.get_index()
        client.close()

    def test_client_session_headers(self):
        """Test that client sets correct headers."""
        client = EOLClient()
        if "User-Agent" not in client.session.headers:
            raise AssertionError
        if "eol-cli" not in client.session.headers["User-Agent"]:
            raise AssertionError
        if not (client.session.headers["Accept"] == "application/json"):
            raise AssertionError
        client.close()

    def test_request_retry_error_reports_attempt_count(self, monkeypatch):
        """Test that retry errors report both retries and total attempts."""
        client = EOLClient()
        call_count = 0

        def _failing_get(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            raise requests.RequestException("transient issue")

        monkeypatch.setattr(client.session, "get", _failing_get)
        monkeypatch.setattr("eol_cli.api.client.time.sleep", lambda _seconds: None)

        with pytest.raises(EOLAPIError) as exc_info:
            client._request("products", max_retries=2)

        client.close()
        if not (call_count == 3):
            raise AssertionError
        if "after 2 retries (3 attempts)" not in str(exc_info.value):
            raise AssertionError
