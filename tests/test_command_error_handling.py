"""Tests for CLI command error handling including API errors, validation errors, and exception paths."""

from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from eol_cli.api.client import EOLAPIError, EOLClient, EOLRateLimitError
from eol_cli.commands.categories import categories
from eol_cli.commands.identifiers import identifiers
from eol_cli.commands.index import index
from eol_cli.commands.products import products
from eol_cli.commands.tags import tags


class TestCategoriesErrorPaths:
    """Test error paths in categories command."""

    def test_categories_list_json_xml_exclusive(self):
        """Test categories list with both --json and --xml flags - lines 36-37."""
        runner = CliRunner()
        result = runner.invoke(categories, ["list", "--json", "--xml"])
        assert result.exit_code == 1
        assert "mutually exclusive" in result.output.lower()

    def test_categories_list_api_error(self):
        """Test categories list with API error - lines 51-53."""
        runner = CliRunner()
        with patch("eol_cli.commands.categories.EOLClient") as mock_client:
            mock_instance = MagicMock()
            mock_instance.list_categories.side_effect = EOLAPIError("API Error")
            mock_client.return_value = mock_instance

            result = runner.invoke(categories, ["list"])
            assert result.exit_code == 1
            assert "error" in result.output.lower()

    def test_categories_get_json_xml_exclusive(self):
        """Test categories get with both --json and --xml flags - lines 84-85."""
        runner = CliRunner()
        result = runner.invoke(categories, ["get", "os", "--json", "--xml"])
        assert result.exit_code == 1
        assert "mutually exclusive" in result.output.lower()

    def test_categories_get_api_error(self):
        """Test categories get with API error - lines 103-105."""
        runner = CliRunner()
        with patch("eol_cli.commands.categories.EOLClient") as mock_client:
            mock_instance = MagicMock()
            mock_instance.get_category_products.side_effect = EOLAPIError("API Error")
            mock_client.return_value = mock_instance

            result = runner.invoke(categories, ["get", "os"])
            assert result.exit_code == 1


class TestTagsErrorPaths:
    """Test error paths in tags command."""

    def test_tags_list_json_xml_exclusive(self):
        """Test tags list with both --json and --xml flags - lines 36-37."""
        runner = CliRunner()
        result = runner.invoke(tags, ["list", "--json", "--xml"])
        assert result.exit_code == 1
        assert "mutually exclusive" in result.output.lower()

    def test_tags_list_api_error(self):
        """Test tags list with API error - lines 51-53."""
        runner = CliRunner()
        with patch("eol_cli.commands.tags.EOLClient") as mock_client:
            mock_instance = MagicMock()
            mock_instance.list_tags.side_effect = EOLAPIError("API Error")
            mock_client.return_value = mock_instance

            result = runner.invoke(tags, ["list"])
            assert result.exit_code == 1

    def test_tags_get_json_xml_exclusive(self):
        """Test tags get with both --json and --xml flags - lines 84-85."""
        runner = CliRunner()
        result = runner.invoke(tags, ["get", "linux-distribution", "--json", "--xml"])
        assert result.exit_code == 1
        assert "mutually exclusive" in result.output.lower()

    def test_tags_get_api_error(self):
        """Test tags get with API error - lines 103-105."""
        runner = CliRunner()
        with patch("eol_cli.commands.tags.EOLClient") as mock_client:
            mock_instance = MagicMock()
            mock_instance.get_tag_products.side_effect = EOLAPIError("API Error")
            mock_client.return_value = mock_instance

            result = runner.invoke(tags, ["get", "test-tag"])
            assert result.exit_code == 1


class TestIdentifiersErrorPaths:
    """Test error paths in identifiers command."""

    def test_identifiers_list_json_xml_exclusive(self):
        """Test identifiers list with both --json and --xml flags - lines 38-39."""
        runner = CliRunner()
        result = runner.invoke(identifiers, ["list", "--json", "--xml"])
        assert result.exit_code == 1
        assert "mutually exclusive" in result.output.lower()

    def test_identifiers_list_api_error(self):
        """Test identifiers list with API error - lines 53-55."""
        runner = CliRunner()
        with patch("eol_cli.commands.identifiers.EOLClient") as mock_client:
            mock_instance = MagicMock()
            mock_instance.list_identifier_types.side_effect = EOLAPIError("API Error")
            mock_client.return_value = mock_instance

            result = runner.invoke(identifiers, ["list"])
            assert result.exit_code == 1

    def test_identifiers_get_json_xml_exclusive(self):
        """Test identifiers get with both --json and --xml flags - lines 86-87."""
        runner = CliRunner()
        result = runner.invoke(identifiers, ["get", "purl", "--json", "--xml"])
        assert result.exit_code == 1
        assert "mutually exclusive" in result.output.lower()

    def test_identifiers_get_api_error(self):
        """Test identifiers get with API error - lines 105-107."""
        runner = CliRunner()
        with patch("eol_cli.commands.identifiers.EOLClient") as mock_client:
            mock_instance = MagicMock()
            mock_instance.get_identifiers_by_type.side_effect = EOLAPIError("API Error")
            mock_client.return_value = mock_instance

            result = runner.invoke(identifiers, ["get", "purl"])
            assert result.exit_code == 1


class TestIndexErrorPaths:
    """Test error paths in index command."""

    def test_index_json_xml_exclusive(self):
        """Test index with both --json and --xml flags - lines 24-25."""
        runner = CliRunner()
        result = runner.invoke(index, ["--json", "--xml"])
        assert result.exit_code == 1
        assert "mutually exclusive" in result.output.lower()

    def test_index_api_error(self):
        """Test index with API error - lines 39-41."""
        runner = CliRunner()
        with patch("eol_cli.commands.index.EOLClient") as mock_client:
            mock_instance = MagicMock()
            mock_instance.get_index.side_effect = EOLAPIError("API Error")
            mock_client.return_value = mock_instance

            result = runner.invoke(index, [])
            assert result.exit_code == 1


class TestProductsErrorPaths:
    """Test error paths in products command."""

    def test_products_list_json_xml_exclusive(self):
        """Test products list with both --json and --xml flags - lines 69-71."""
        runner = CliRunner()
        result = runner.invoke(products, ["list", "--json", "--xml"])
        assert result.exit_code == 1
        assert "mutually exclusive" in result.output.lower()

    def test_products_list_api_error(self):
        """Test products list with API error - lines 113-114."""
        runner = CliRunner()
        with patch("eol_cli.commands.products.EOLClient") as mock_client:
            mock_instance = MagicMock()
            mock_instance.list_products.side_effect = EOLAPIError("API Error")
            mock_client.return_value = mock_instance

            result = runner.invoke(products, ["list"])
            assert result.exit_code == 1

    def test_products_get_json_xml_exclusive(self):
        """Test products get with both --json and --xml flags - lines 132-133."""
        runner = CliRunner()
        result = runner.invoke(products, ["get", "python", "--json", "--xml"])
        assert result.exit_code == 1
        assert "mutually exclusive" in result.output.lower()

    def test_products_get_api_error_single(self):
        """Test products get with API error for single product - lines 213-214."""
        runner = CliRunner()
        with patch("eol_cli.commands.products.EOLClient") as mock_client:
            mock_instance = MagicMock()
            mock_instance.get_product.side_effect = EOLAPIError("API Error")
            mock_client.return_value = mock_instance

            result = runner.invoke(products, ["get", "python"])
            assert result.exit_code == 1

    def test_products_release_json_xml_exclusive(self):
        """Test products release with both --json and --xml flags - lines 241-243."""
        runner = CliRunner()
        result = runner.invoke(products, ["release", "python", "latest", "--json", "--xml"])
        assert result.exit_code == 1
        assert "mutually exclusive" in result.output.lower()


class TestAPIClientErrorHandling:
    """Test API client error handling for lines 70-71, 81, 85."""

    def test_rate_limit_error_creation(self):
        """Test rate limit error with retry-after header - lines 70-71."""
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
        """Test HTTP error handling - line 81."""
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
        """Test JSON parsing error - line 85."""
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
    """Test products release command API error - lines 241-243."""

    def test_products_release_api_error(self):
        """Test products release with API error."""
        runner = CliRunner()
        with patch("eol_cli.commands.products.EOLClient") as mock_client:
            mock_instance = MagicMock()
            mock_instance.get_product_release.side_effect = EOLAPIError("API Error")
            mock_client.return_value = mock_instance

            result = runner.invoke(products, ["release", "python", "3.11"])
            assert result.exit_code == 1
            assert "error" in result.output.lower()


class TestCLIMainErrorPath:
    """Test CLI main error path - line 49."""

    def test_cli_exception_handling(self):
        """Test CLI exception handling."""
        from eol_cli.cli import main

        runner = CliRunner()
        # Test with an option that doesn't exist
        result = runner.invoke(main, ["--nonexistent-option"])
        assert result.exit_code != 0

    def test_cli_main_direct_execution(self):
        """Test CLI main function direct execution - line 49."""
        import subprocess

        result = subprocess.run(
            ["python", "-m", "eol_cli.cli", "--version"],
            capture_output=True,
            text=True,
            cwd="/Users/seifreed/tools/pentest/eol-cli",
        )
        assert result.returncode == 0
        assert "0.1.0" in result.stdout or "0.1.0" in result.stderr
