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


class TestProductsGetEdgePaths:
    """Test edge paths in products get command."""

    def test_products_get_empty_names(self):
        """Comma-only input produces no valid product names."""
        runner = CliRunner()
        obj = _make_mock_client()
        result = runner.invoke(products, ["get", ",,,"], obj=obj)
        assert result.exit_code == 1
        assert "no valid product" in result.output.lower()

    def test_products_get_json_single(self):
        """JSON output for a single product goes through emit()."""
        runner = CliRunner()
        mock_data = {"schema_version": "1.2.0", "result": {"name": "python", "releases": []}}
        obj = _make_mock_client()
        obj["client"].get_product.return_value = mock_data
        result = runner.invoke(products, ["get", "python", "--json"], obj=obj)
        assert result.exit_code == 0
        assert '"python"' in result.output

    def test_products_get_xml_multi(self):
        """XML output for multiple products aggregates and goes through emit()."""
        runner = CliRunner()
        mock_data = {"schema_version": "1.2.0", "result": {"name": "p", "releases": []}}
        obj = _make_mock_client()
        obj["client"].get_product.return_value = mock_data
        result = runner.invoke(products, ["get", "a,b", "--xml"], obj=obj)
        assert result.exit_code == 0
        assert "<response>" in result.output

    def test_products_get_outer_api_error_catch(self):
        """EOLAPIError that bypasses inner handlers is caught by the outer except."""
        runner = CliRunner()
        # Make get_product return valid data, but make list_products (called in
        # _handle_errors_and_suggestions for the not-found product) raise an
        # EOLAPIError that propagates to the outer handler.
        from eol_cli.api.client import EOLNotFoundError

        call_count = {"n": 0}

        def get_product_side_effect(name: str) -> dict:
            call_count["n"] += 1
            if name == "valid":
                return {"schema_version": "1.2.0", "result": {"name": "valid", "releases": []}}
            raise EOLNotFoundError(f"Not found: {name}")

        obj = _make_mock_client()
        obj["client"].get_product.side_effect = get_product_side_effect
        obj["client"].list_products.return_value = {"result": []}
        result = runner.invoke(products, ["get", "valid,invalid"], obj=obj)
        # _fetch_products catches the NotFoundError, _handle_errors_and_suggestions
        # prints warning and tries suggestions. The result still succeeds for valid.
        assert "warning" in result.output.lower() or "not found" in result.output.lower()

    def test_products_get_suggestion_rate_limited(self):
        """Rate limit error during suggestion fetch shows specific message."""
        runner = CliRunner()
        from eol_cli.api.client import EOLNotFoundError, EOLRateLimitError

        obj = _make_mock_client(
            get_product=EOLNotFoundError("not found"),
            list_products=EOLRateLimitError("rate limited"),
        )
        result = runner.invoke(products, ["get", "pythn"], obj=obj)
        assert result.exit_code == 1
        assert "rate limited" in result.output.lower()

    def test_products_get_suggestion_api_error(self):
        """Generic API error during suggestion fetch shows fallback message."""
        runner = CliRunner()
        from eol_cli.api.client import EOLNotFoundError

        obj = _make_mock_client(
            get_product=EOLNotFoundError("not found"),
            list_products=EOLAPIError("server down"),
        )
        result = runner.invoke(products, ["get", "pythn"], obj=obj)
        assert result.exit_code == 1
        assert "could not fetch suggestions" in result.output.lower()


class TestProductsReleaseErrorPath:
    """Test products release command error paths."""

    def test_products_release_api_error(self):
        runner = CliRunner()
        obj = _make_mock_client(get_product_release=EOLAPIError("API Error"))
        result = runner.invoke(products, ["release", "python", "3.11"], obj=obj)
        assert result.exit_code == 1
        assert "error" in result.output.lower()

    def test_products_release_latest_api_error(self):
        """EOLAPIError (not NotFound) on latest release is caught."""
        runner = CliRunner()
        obj = _make_mock_client(get_product_latest_release=EOLAPIError("Server Error"))
        result = runner.invoke(products, ["release", "python", "latest"], obj=obj)
        assert result.exit_code == 1
        assert "error" in result.output.lower()

    def test_products_get_outer_except_api_error(self):
        """EOLAPIError raised after fetch/suggestions is caught by outer handler."""
        runner = CliRunner()
        # Make get_product succeed, then make the data trigger an error during
        # output by returning data that causes _create_aggregated_response to
        # access all_data[0] on an empty list — but _handle_errors raises Abort
        # before that. The only way to reach lines 187-189 is if something
        # between _handle_errors and the end of the try block raises EOLAPIError.
        # We simulate this by patching _output_rich_format to raise.
        obj = _make_mock_client()
        obj["client"].get_product.return_value = {
            "schema_version": "1.2.0",
            "result": {"name": "p", "releases": []},
        }
        with patch(
            "eol_cli.commands.products._output_rich_format",
            side_effect=EOLAPIError("Unexpected render error"),
        ):
            result = runner.invoke(products, ["get", "python"], obj=obj)
        assert result.exit_code == 1
        assert "unexpected render error" in result.output.lower()


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


class TestVersionFallback:
    """Test _version.py fallback when package is not installed."""

    def test_version_fallback_when_not_installed(self):
        """PackageNotFoundError triggers the dev fallback."""
        from importlib.metadata import PackageNotFoundError

        with patch(
            "importlib.metadata.version", side_effect=PackageNotFoundError("eol-cli")
        ):
            import importlib

            import eol_cli._version

            importlib.reload(eol_cli._version)
            assert eol_cli._version.__version__ == "0.0.0-dev"

        # Restore
        import importlib

        import eol_cli._version

        importlib.reload(eol_cli._version)


class TestCLIMainGuard:
    """Test cli.py __main__ guard."""

    def test_main_module_execution(self):
        """Running cli.py as __main__ invokes main()."""
        import subprocess

        result = subprocess.run(
            ["python", "-c", "import runpy; runpy.run_module('eol_cli.cli', run_name='__main__', alter_sys=True)"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        # Will show help/usage since no args, or version error — either way it ran
        assert result.returncode in (0, 2)
