"""Tests for CLI command error handling including API errors, validation errors, and exception paths."""

import pathlib
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from eol_cli.api.client import EOLAPIError, EOLClient, EOLRateLimitError
from eol_cli.commands.categories import categories
from eol_cli.commands.identifiers import identifiers
from eol_cli.commands.index import index
from eol_cli.commands.products import products
from eol_cli.commands.tags import tags


def _make_mock_client(**overrides):
    """Create a mock client dict for Click context injection."""
    client = MagicMock()
    for attr, side_effect in overrides.items():
        getattr(client, attr).side_effect = side_effect
    return {"client": client}


class TestCategoriesErrorPaths:
    """Test error paths in categories command."""

    def test_categories_list_json_xml_exclusive(self):
        runner = CliRunner()
        obj = _make_mock_client()
        result = runner.invoke(categories, ["list", "--json", "--xml"], obj=obj)
        assert result.exit_code == 2
        assert "mutually exclusive" in result.output.lower()

    def test_categories_list_api_error(self):
        runner = CliRunner()
        obj = _make_mock_client(list_categories=EOLAPIError("API Error"))
        result = runner.invoke(categories, ["list"], obj=obj)
        assert result.exit_code == 1
        assert "error" in result.output.lower()

    def test_categories_get_json_xml_exclusive(self):
        runner = CliRunner()
        obj = _make_mock_client()
        result = runner.invoke(categories, ["get", "os", "--json", "--xml"], obj=obj)
        assert result.exit_code == 2
        assert "mutually exclusive" in result.output.lower()

    def test_categories_get_api_error(self):
        runner = CliRunner()
        obj = _make_mock_client(get_category_products=EOLAPIError("API Error"))
        result = runner.invoke(categories, ["get", "os"], obj=obj)
        assert result.exit_code == 1


class TestTagsErrorPaths:
    """Test error paths in tags command."""

    def test_tags_list_json_xml_exclusive(self):
        runner = CliRunner()
        obj = _make_mock_client()
        result = runner.invoke(tags, ["list", "--json", "--xml"], obj=obj)
        assert result.exit_code == 2
        assert "mutually exclusive" in result.output.lower()

    def test_tags_list_api_error(self):
        runner = CliRunner()
        obj = _make_mock_client(list_tags=EOLAPIError("API Error"))
        result = runner.invoke(tags, ["list"], obj=obj)
        assert result.exit_code == 1

    def test_tags_get_json_xml_exclusive(self):
        runner = CliRunner()
        obj = _make_mock_client()
        result = runner.invoke(tags, ["get", "linux-distribution", "--json", "--xml"], obj=obj)
        assert result.exit_code == 2
        assert "mutually exclusive" in result.output.lower()

    def test_tags_get_api_error(self):
        runner = CliRunner()
        obj = _make_mock_client(get_tag_products=EOLAPIError("API Error"))
        result = runner.invoke(tags, ["get", "test-tag"], obj=obj)
        assert result.exit_code == 1


class TestIdentifiersErrorPaths:
    """Test error paths in identifiers command."""

    def test_identifiers_list_json_xml_exclusive(self):
        runner = CliRunner()
        obj = _make_mock_client()
        result = runner.invoke(identifiers, ["list", "--json", "--xml"], obj=obj)
        assert result.exit_code == 2
        assert "mutually exclusive" in result.output.lower()

    def test_identifiers_list_api_error(self):
        runner = CliRunner()
        obj = _make_mock_client(list_identifier_types=EOLAPIError("API Error"))
        result = runner.invoke(identifiers, ["list"], obj=obj)
        assert result.exit_code == 1

    def test_identifiers_get_json_xml_exclusive(self):
        runner = CliRunner()
        obj = _make_mock_client()
        result = runner.invoke(identifiers, ["get", "purl", "--json", "--xml"], obj=obj)
        assert result.exit_code == 2
        assert "mutually exclusive" in result.output.lower()

    def test_identifiers_get_api_error(self):
        runner = CliRunner()
        obj = _make_mock_client(get_identifiers_by_type=EOLAPIError("API Error"))
        result = runner.invoke(identifiers, ["get", "purl"], obj=obj)
        assert result.exit_code == 1


class TestIndexErrorPaths:
    """Test error paths in index command."""

    def test_index_json_xml_exclusive(self):
        runner = CliRunner()
        obj = _make_mock_client()
        result = runner.invoke(index, ["--json", "--xml"], obj=obj)
        assert result.exit_code == 2
        assert "mutually exclusive" in result.output.lower()

    def test_index_api_error(self):
        runner = CliRunner()
        obj = _make_mock_client(get_index=EOLAPIError("API Error"))
        result = runner.invoke(index, [], obj=obj)
        assert result.exit_code == 1


class TestProductsErrorPaths:
    """Test error paths in products command."""

    def test_products_list_json_xml_exclusive(self):
        runner = CliRunner()
        obj = _make_mock_client()
        result = runner.invoke(products, ["list", "--json", "--xml"], obj=obj)
        assert result.exit_code == 2
        assert "mutually exclusive" in result.output.lower()

    def test_products_list_api_error(self):
        runner = CliRunner()
        obj = _make_mock_client(list_products=EOLAPIError("API Error"))
        result = runner.invoke(products, ["list"], obj=obj)
        assert result.exit_code == 1

    def test_products_get_json_xml_exclusive(self):
        runner = CliRunner()
        obj = _make_mock_client()
        result = runner.invoke(products, ["get", "python", "--json", "--xml"], obj=obj)
        assert result.exit_code == 2
        assert "mutually exclusive" in result.output.lower()

    def test_products_get_api_error_single(self):
        runner = CliRunner()
        obj = _make_mock_client(get_product=EOLAPIError("API Error"))
        result = runner.invoke(products, ["get", "python"], obj=obj)
        assert result.exit_code == 1

    def test_products_release_json_xml_exclusive(self):
        runner = CliRunner()
        obj = _make_mock_client()
        result = runner.invoke(products, ["release", "python", "latest", "--json", "--xml"], obj=obj)
        assert result.exit_code == 2
        assert "mutually exclusive" in result.output.lower()


@pytest.mark.api
class TestAPIClientErrorHandling:
    """Test API client error handling."""

    def test_rate_limit_error_creation(self):
        with patch("eol_cli.api.client.requests.Session.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 429
            mock_response.headers = {"Retry-After": "60"}
            mock_get.return_value = mock_response

            client = EOLClient()
            with pytest.raises(EOLRateLimitError) as exc_info:
                client._request("/test")

            assert "60" in str(exc_info.value)
            client.close()

    def test_http_error_handling(self):
        from requests.exceptions import HTTPError

        with patch("eol_cli.api.client.requests.Session.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_response.raise_for_status.side_effect = HTTPError("HTTP Error 500")
            mock_get.return_value = mock_response

            client = EOLClient()
            with pytest.raises(EOLAPIError):
                client._request("/test")

            client.close()

    def test_json_value_error_handling(self):
        with patch("eol_cli.api.client.requests.Session.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.side_effect = ValueError("Invalid JSON")
            mock_get.return_value = mock_response

            client = EOLClient()
            with pytest.raises(EOLAPIError) as exc_info:
                client._request("/test")

            assert "Invalid JSON" in str(exc_info.value)
            client.close()


class TestProductsReleaseErrorPath:
    """Test products release command API error."""

    def test_products_release_api_error(self):
        runner = CliRunner()
        obj = _make_mock_client(get_product_release=EOLAPIError("API Error"))
        result = runner.invoke(products, ["release", "python", "3.11"], obj=obj)
        assert result.exit_code == 1
        assert "error" in result.output.lower()


class TestCLIMainErrorPath:
    """Test CLI main error path."""

    def test_cli_exception_handling(self):
        from eol_cli.cli import main

        runner = CliRunner()
        result = runner.invoke(main, ["--nonexistent-option"])
        assert result.exit_code != 0

    def test_cli_main_direct_execution(self):
        from eol_cli.cli import main

        runner = CliRunner()
        result = runner.invoke(main, ["--version"])
        assert result.exit_code == 0
        assert "0.1.0" in result.output
