"""Tests for the API client -"""

import pytest

from eol_cli.api.client import EOLAPIError, EOLClient, EOLNotFoundError


class TestEOLClient:
    """Test suite for EOLClient."""

    def test_client_initialization(self):
        """Test that the client initializes correctly."""
        client = EOLClient()
        assert client.base_url == EOLClient.BASE_URL
        assert client.timeout == 30
        client.close()

    def test_client_custom_base_url(self):
        """Test client with custom base URL."""
        custom_url = "https://example.com/api"
        client = EOLClient(base_url=custom_url)
        assert client.base_url == custom_url
        client.close()

    def test_client_custom_timeout(self):
        """Test client with custom timeout."""
        client = EOLClient(timeout=60)
        assert client.timeout == 60
        client.close()

    def test_client_context_manager(self):
        """Test client as context manager."""
        with EOLClient() as client:
            assert client is not None
            assert client.session is not None


class TestIndexEndpoint:
    """Test index endpoint."""

    def test_get_index_returns_valid_data(self):
        """Test that get_index returns valid data."""
        with EOLClient() as client:
            data = client.get_index()
            assert "schema_version" in data
            assert "total" in data
            assert "result" in data
            assert isinstance(data["result"], list)
            assert data["total"] > 0

            # Verify structure of URI items
            for item in data["result"]:
                assert "name" in item
                assert "uri" in item


class TestProductsEndpoints:
    """Test products endpoints with real API calls."""

    def test_list_products_returns_valid_data(self):
        """Test that list_products returns valid data."""
        with EOLClient() as client:
            data = client.list_products()
            assert "schema_version" in data
            assert "total" in data
            assert "result" in data
            assert isinstance(data["result"], list)
            assert data["total"] > 0

            # Verify first product has expected fields
            product = data["result"][0]
            assert "name" in product
            assert "label" in product
            assert "category" in product
            assert "tags" in product
            assert isinstance(product["tags"], list)

    def test_list_products_full_returns_complete_data(self):
        """Test that list_products_full returns complete product data."""
        with EOLClient() as client:
            data = client.list_products_full()
            assert "schema_version" in data
            assert "total" in data
            assert "result" in data
            assert isinstance(data["result"], list)

            # Verify full product has releases
            product = data["result"][0]
            assert "releases" in product
            assert isinstance(product["releases"], list)

    def test_get_product_python_returns_valid_data(self):
        """Test get_product for Python returns valid data."""
        with EOLClient() as client:
            data = client.get_product("python")
            assert "schema_version" in data
            assert "last_modified" in data
            assert "result" in data

            result = data["result"]
            assert result["name"] == "python"
            assert "releases" in result
            assert isinstance(result["releases"], list)
            assert len(result["releases"]) > 0
            assert "label" in result
            assert "category" in result
            assert "tags" in result

    def test_get_product_ubuntu_returns_valid_data(self):
        """Test get_product for Ubuntu returns valid data."""
        with EOLClient() as client:
            data = client.get_product("ubuntu")
            assert data["result"]["name"] == "ubuntu"
            assert len(data["result"]["releases"]) > 0

    def test_get_product_not_found_raises_exception(self):
        """Test that getting a non-existent product raises EOLNotFoundError."""
        with EOLClient() as client:
            with pytest.raises(EOLNotFoundError):
                client.get_product("this-product-does-not-exist-12345")

    def test_get_product_release_python_returns_valid_data(self):
        """Test get_product_release for Python 3.11."""
        with EOLClient() as client:
            data = client.get_product_release("python", "3.11")
            assert "schema_version" in data
            assert "result" in data

            result = data["result"]
            assert result["name"] == "3.11"
            assert "releaseDate" in result
            assert "isEol" in result
            assert "eolFrom" in result
            assert "latest" in result

    def test_get_product_release_not_found_raises_exception(self):
        """Test that non-existent release raises EOLNotFoundError."""
        with EOLClient() as client:
            with pytest.raises(EOLNotFoundError):
                client.get_product_release("python", "99.99")

    def test_get_product_latest_release_python(self):
        """Test get_product_latest_release for Python."""
        with EOLClient() as client:
            data = client.get_product_latest_release("python")
            assert "schema_version" in data
            assert "result" in data

            result = data["result"]
            assert "name" in result
            assert "releaseDate" in result
            assert "isEol" in result

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
            assert "schema_version" in data
            assert "total" in data
            assert "result" in data
            assert isinstance(data["result"], list)
            assert data["total"] > 0

            # Verify category has expected fields
            category = data["result"][0]
            assert "name" in category
            assert "uri" in category

    def test_get_category_products_os_returns_valid_data(self):
        """Test get_category_products for 'os' category."""
        with EOLClient() as client:
            data = client.get_category_products("os")
            assert "schema_version" in data
            assert "total" in data
            assert "result" in data
            assert isinstance(data["result"], list)
            assert data["total"] > 0

            # Verify all products are in 'os' category
            for product in data["result"]:
                assert product["category"] == "os"

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
            assert "schema_version" in data
            assert "total" in data
            assert "result" in data
            assert isinstance(data["result"], list)
            assert data["total"] > 0

    def test_get_tag_products_linux_distribution_returns_valid_data(self):
        """Test get_tag_products for 'linux-distribution'."""
        with EOLClient() as client:
            data = client.get_tag_products("linux-distribution")
            assert "schema_version" in data
            assert "total" in data
            assert "result" in data
            assert isinstance(data["result"], list)
            assert data["total"] > 0

            # Verify all products have the tag
            for product in data["result"]:
                assert "linux-distribution" in product["tags"]

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
            assert "schema_version" in data
            assert "total" in data
            assert "result" in data
            assert isinstance(data["result"], list)
            assert data["total"] > 0

    def test_get_identifiers_by_type_purl_returns_valid_data(self):
        """Test get_identifiers_by_type for 'purl'."""
        with EOLClient() as client:
            data = client.get_identifiers_by_type("purl")
            assert "schema_version" in data
            assert "total" in data
            assert "result" in data
            assert isinstance(data["result"], list)
            assert data["total"] > 0

            # Verify identifier structure
            identifier_entry = data["result"][0]
            assert "identifier" in identifier_entry
            assert "product" in identifier_entry
            assert "name" in identifier_entry["product"]
            assert "uri" in identifier_entry["product"]

    def test_get_identifiers_by_type_cpe_returns_valid_data(self):
        """Test get_identifiers_by_type for 'cpe'."""
        with EOLClient() as client:
            data = client.get_identifiers_by_type("cpe")
            assert "total" in data
            assert data["total"] > 0

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
        assert "User-Agent" in client.session.headers
        assert "eol-cli" in client.session.headers["User-Agent"]
        assert client.session.headers["Accept"] == "application/json"
        client.close()
