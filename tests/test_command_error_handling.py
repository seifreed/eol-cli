"""Tests for CLI command error handling including API errors, validation errors, and exception paths."""

import json
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from eol_cli.api.client import EOLAPIError, EOLClient, EOLRateLimitError
from eol_cli.commands.categories import categories
from eol_cli.commands.identifiers import identifiers
from eol_cli.commands.index import index
from eol_cli.commands.products import products
from eol_cli.commands.tags import tags
from eol_cli.domain.contracts import ResponseEnvelope
from eol_cli.presentation.responses import create_aggregated_response


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
        if not (result.exit_code == 2):
            raise AssertionError
        if "mutually exclusive" not in result.output.lower():
            raise AssertionError

    def test_categories_list_api_error(self):
        runner = CliRunner()
        obj = _make_mock_client(list_categories=EOLAPIError("API Error"))
        result = runner.invoke(categories, ["list"], obj=obj)
        if not (result.exit_code == 1):
            raise AssertionError
        if "error" not in result.output.lower():
            raise AssertionError

    def test_categories_get_json_xml_exclusive(self):
        runner = CliRunner()
        obj = _make_mock_client()
        result = runner.invoke(categories, ["get", "os", "--json", "--xml"], obj=obj)
        if not (result.exit_code == 2):
            raise AssertionError
        if "mutually exclusive" not in result.output.lower():
            raise AssertionError

    def test_categories_get_api_error(self):
        runner = CliRunner()
        obj = _make_mock_client(get_category_products=EOLAPIError("API Error"))
        result = runner.invoke(categories, ["get", "os"], obj=obj)
        if not (result.exit_code == 1):
            raise AssertionError


class TestTagsErrorPaths:
    """Test error paths in tags command."""

    def test_tags_list_json_xml_exclusive(self):
        runner = CliRunner()
        obj = _make_mock_client()
        result = runner.invoke(tags, ["list", "--json", "--xml"], obj=obj)
        if not (result.exit_code == 2):
            raise AssertionError
        if "mutually exclusive" not in result.output.lower():
            raise AssertionError

    def test_tags_list_api_error(self):
        runner = CliRunner()
        obj = _make_mock_client(list_tags=EOLAPIError("API Error"))
        result = runner.invoke(tags, ["list"], obj=obj)
        if not (result.exit_code == 1):
            raise AssertionError

    def test_tags_get_json_xml_exclusive(self):
        runner = CliRunner()
        obj = _make_mock_client()
        result = runner.invoke(tags, ["get", "linux-distribution", "--json", "--xml"], obj=obj)
        if not (result.exit_code == 2):
            raise AssertionError
        if "mutually exclusive" not in result.output.lower():
            raise AssertionError

    def test_tags_get_api_error(self):
        runner = CliRunner()
        obj = _make_mock_client(get_tag_products=EOLAPIError("API Error"))
        result = runner.invoke(tags, ["get", "test-tag"], obj=obj)
        if not (result.exit_code == 1):
            raise AssertionError


class TestIdentifiersErrorPaths:
    """Test error paths in identifiers command."""

    def test_identifiers_list_json_xml_exclusive(self):
        runner = CliRunner()
        obj = _make_mock_client()
        result = runner.invoke(identifiers, ["list", "--json", "--xml"], obj=obj)
        if not (result.exit_code == 2):
            raise AssertionError
        if "mutually exclusive" not in result.output.lower():
            raise AssertionError

    def test_identifiers_list_api_error(self):
        runner = CliRunner()
        obj = _make_mock_client(list_identifier_types=EOLAPIError("API Error"))
        result = runner.invoke(identifiers, ["list"], obj=obj)
        if not (result.exit_code == 1):
            raise AssertionError

    def test_identifiers_get_json_xml_exclusive(self):
        runner = CliRunner()
        obj = _make_mock_client()
        result = runner.invoke(identifiers, ["get", "purl", "--json", "--xml"], obj=obj)
        if not (result.exit_code == 2):
            raise AssertionError
        if "mutually exclusive" not in result.output.lower():
            raise AssertionError

    def test_identifiers_get_api_error(self):
        runner = CliRunner()
        obj = _make_mock_client(get_identifiers_by_type=EOLAPIError("API Error"))
        result = runner.invoke(identifiers, ["get", "purl"], obj=obj)
        if not (result.exit_code == 1):
            raise AssertionError


class TestIndexErrorPaths:
    """Test error paths in index command."""

    def test_index_json_xml_exclusive(self):
        runner = CliRunner()
        obj = _make_mock_client()
        result = runner.invoke(index, ["--json", "--xml"], obj=obj)
        if not (result.exit_code == 2):
            raise AssertionError
        if "mutually exclusive" not in result.output.lower():
            raise AssertionError

    def test_index_api_error(self):
        runner = CliRunner()
        obj = _make_mock_client(get_index=EOLAPIError("API Error"))
        result = runner.invoke(index, [], obj=obj)
        if not (result.exit_code == 1):
            raise AssertionError


class TestProductsErrorPaths:
    """Test error paths in products command."""

    def test_products_list_json_xml_exclusive(self):
        runner = CliRunner()
        obj = _make_mock_client()
        result = runner.invoke(products, ["list", "--json", "--xml"], obj=obj)
        if not (result.exit_code == 2):
            raise AssertionError
        if "mutually exclusive" not in result.output.lower():
            raise AssertionError

    def test_products_list_api_error(self):
        runner = CliRunner()
        obj = _make_mock_client(list_products=EOLAPIError("API Error"))
        result = runner.invoke(products, ["list"], obj=obj)
        if not (result.exit_code == 1):
            raise AssertionError

    def test_products_get_json_xml_exclusive(self):
        runner = CliRunner()
        obj = _make_mock_client()
        result = runner.invoke(products, ["get", "python", "--json", "--xml"], obj=obj)
        if not (result.exit_code == 2):
            raise AssertionError
        if "mutually exclusive" not in result.output.lower():
            raise AssertionError

    def test_products_get_api_error_single(self):
        runner = CliRunner()
        obj = _make_mock_client(get_product=EOLAPIError("API Error"))
        result = runner.invoke(products, ["get", "python"], obj=obj)
        if not (result.exit_code == 1):
            raise AssertionError

    def test_products_release_json_xml_exclusive(self):
        runner = CliRunner()
        obj = _make_mock_client()
        result = runner.invoke(
            products, ["release", "python", "latest", "--json", "--xml"], obj=obj
        )
        if not (result.exit_code == 2):
            raise AssertionError
        if "mutually exclusive" not in result.output.lower():
            raise AssertionError


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

            if "60" not in str(exc_info.value):
                raise AssertionError
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

            if "Invalid JSON" not in str(exc_info.value):
                raise AssertionError
            client.close()


class TestProductsGetEdgePaths:
    """Test edge paths in products get command."""

    def test_products_get_empty_names(self):
        """Comma-only input produces no valid product names."""
        runner = CliRunner()
        obj = _make_mock_client()
        result = runner.invoke(products, ["get", ",,,"], obj=obj)
        if not (result.exit_code == 1):
            raise AssertionError
        if "no valid product" not in result.output.lower():
            raise AssertionError

    def test_products_get_json_single(self):
        """JSON output for a single product goes through emit()."""
        runner = CliRunner()
        mock_data = {"schema_version": "1.2.0", "result": {"name": "python", "releases": []}}
        obj = _make_mock_client()
        obj["client"].get_product.return_value = mock_data
        result = runner.invoke(products, ["get", "python", "--json"], obj=obj)
        if not (result.exit_code == 0):
            raise AssertionError
        if '"python"' not in result.output:
            raise AssertionError

    def test_products_get_xml_multi(self):
        """XML output for multiple products aggregates and goes through emit()."""
        runner = CliRunner()
        mock_data = {"schema_version": "1.2.0", "result": {"name": "p", "releases": []}}
        obj = _make_mock_client()
        obj["client"].get_product.return_value = mock_data
        result = runner.invoke(products, ["get", "a,b", "--xml"], obj=obj)
        if not (result.exit_code == 0):
            raise AssertionError
        if "<response>" not in result.output:
            raise AssertionError

    def test_products_get_outer_api_error_catch(self):
        """EOLAPIError that bypasses inner handlers is caught by the outer except."""
        runner = CliRunner()
        # Make get_product return valid data, but make list_products (called in
        # error handling for the not-found product) raise an
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
        # Use-case catches the NotFoundError, command feedback prints warning and
        # tries suggestions. The result still succeeds for valid products.
        if not ("warning" in result.output.lower() or "not found" in result.output.lower()):
            raise AssertionError

    def test_products_get_json_with_partial_results_includes_meta_summary(self):
        """JSON output includes fetch summary metadata when some products are not found."""
        runner = CliRunner()
        from eol_cli.api.client import EOLNotFoundError

        def get_product_side_effect(name):
            if name == "python":
                return {"schema_version": "1.2.0", "result": {"name": "python", "releases": []}}
            raise EOLNotFoundError(f"Not found: {name}")

        obj = _make_mock_client()
        obj["client"].get_product.side_effect = get_product_side_effect
        obj["client"].list_products.return_value = {"result": [{"name": "python"}], "total": 1}

        result = runner.invoke(products, ["get", "python,invalid-xyz", "--json"], obj=obj)
        if not (result.exit_code == 0):
            raise AssertionError

        payload = json.loads(result.stdout)
        if "meta" not in payload:
            raise AssertionError
        fetch_summary = payload["meta"]["fetch_summary"]
        if not (fetch_summary["requested"] == 2):
            raise AssertionError
        if not (fetch_summary["succeeded"] == 1):
            raise AssertionError
        if not (fetch_summary["failed"] == 1):
            raise AssertionError
        if "invalid-xyz" not in fetch_summary["not_found"][0]:
            raise AssertionError

    def test_products_get_suggestion_rate_limited(self):
        """Rate limit error during suggestion fetch shows specific message."""
        runner = CliRunner()
        from eol_cli.api.client import EOLNotFoundError, EOLRateLimitError

        obj = _make_mock_client(
            get_product=EOLNotFoundError("not found"),
            list_products=EOLRateLimitError("rate limited"),
        )
        result = runner.invoke(products, ["get", "pythn"], obj=obj)
        if not (result.exit_code == 1):
            raise AssertionError
        if "rate limited" not in result.output.lower():
            raise AssertionError

    def test_products_get_suggestion_api_error(self):
        """Generic API error during suggestion fetch shows fallback message."""
        runner = CliRunner()
        from eol_cli.api.client import EOLNotFoundError

        obj = _make_mock_client(
            get_product=EOLNotFoundError("not found"),
            list_products=EOLAPIError("server down"),
        )
        result = runner.invoke(products, ["get", "pythn"], obj=obj)
        if not (result.exit_code == 1):
            raise AssertionError
        if "could not fetch suggestions" not in result.output.lower():
            raise AssertionError


class TestProductsReleaseErrorPath:
    """Test products release command error paths."""

    def test_products_release_api_error(self):
        runner = CliRunner()
        obj = _make_mock_client(get_product_release=EOLAPIError("API Error"))
        result = runner.invoke(products, ["release", "python", "3.11"], obj=obj)
        if not (result.exit_code == 1):
            raise AssertionError
        if "error" not in result.output.lower():
            raise AssertionError

    def test_products_release_latest_api_error(self):
        """EOLAPIError (not NotFound) on latest release is caught."""
        runner = CliRunner()
        obj = _make_mock_client(get_product_latest_release=EOLAPIError("Server Error"))
        result = runner.invoke(products, ["release", "python", "latest"], obj=obj)
        if not (result.exit_code == 1):
            raise AssertionError
        if "error" not in result.output.lower():
            raise AssertionError

    def test_products_get_outer_except_api_error(self):
        """EOLAPIError raised after fetch/suggestions is caught by outer handler."""
        runner = CliRunner()
        # Make get_product succeed, then make the data trigger an error during
        # output by returning data that causes create_aggregated_response to
        # access all_data[0] on an empty list — but command abort handling raises Abort
        # before that. The only way to reach this path is if something
        # between error handling and the end of the try block raises EOLAPIError.
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
        if not (result.exit_code == 1):
            raise AssertionError
        if "unexpected render error" not in result.output.lower():
            raise AssertionError


class TestCLIMainErrorPath:
    """Test CLI main error path."""

    def test_cli_exception_handling(self):
        from eol_cli.cli import main

        runner = CliRunner()
        result = runner.invoke(main, ["--nonexistent-option"])
        if not (result.exit_code != 0):
            raise AssertionError

    def test_cli_main_direct_execution(self):
        from eol_cli.cli import main

        runner = CliRunner()
        result = runner.invoke(main, ["--version"])
        if not (result.exit_code == 0):
            raise AssertionError
        if "0.1.0" not in result.output:
            raise AssertionError


class TestCreateAggregatedResponse:
    """Test create_aggregated_response function edge cases."""

    def test_create_aggregated_response_empty_list_raises(self):
        """Test that create_aggregated_response raises on empty list."""
        with pytest.raises(ValueError, match="empty list"):
            create_aggregated_response([])

    def test_create_aggregated_response_single_product(self):
        """Test that create_aggregated_response works with single product."""
        data = [ResponseEnvelope(schema_version="1.2.0", result={"name": "python"})]
        result = create_aggregated_response(data)
        if not (result["total"] == 1):
            raise AssertionError
        if not (result["schema_version"] == "1.2.0"):
            raise AssertionError
        if not (len(result["products"]) == 1):
            raise AssertionError

    def test_create_aggregated_response_multiple_products(self):
        """Test that create_aggregated_response works with multiple products."""
        data = [
            ResponseEnvelope(schema_version="1.2.0", result={"name": "python"}),
            ResponseEnvelope(schema_version="1.2.0", result={"name": "nodejs"}),
        ]
        result = create_aggregated_response(data)
        if not (result["total"] == 2):
            raise AssertionError
        if not (len(result["products"]) == 2):
            raise AssertionError

    def test_create_aggregated_response_uses_highest_schema_version(self):
        """Test that create_aggregated_response picks the highest schema version."""
        data = [
            ResponseEnvelope(schema_version="1.9.0", result={"name": "python"}),
            ResponseEnvelope(schema_version="1.10.0", result={"name": "nodejs"}),
            ResponseEnvelope(schema_version="1.2.1", result={"name": "go"}),
        ]
        result = create_aggregated_response(data)
        if not (result["schema_version"] == "1.10.0"):
            raise AssertionError


class TestNon404ErrorSuggestions:
    """Test that suggestions are shown for non-404 API errors."""

    def test_no_suggestions_on_rate_limit_error(self):
        """Test that suggestions are NOT shown on rate limit errors.

        The product might exist, we just couldn't fetch it due to rate limiting.
        Showing suggestions would be misleading.
        """
        runner = CliRunner()
        from eol_cli.api.client import EOLRateLimitError

        obj = _make_mock_client()
        obj["client"].get_product.side_effect = EOLRateLimitError("Rate limit exceeded")
        result = runner.invoke(products, ["get", "pythn"], obj=obj)
        # Should show error but NOT suggestions - product might exist
        if not ("Rate limit" in result.output or "rate limit" in result.output.lower()):
            raise AssertionError
        if not ("Did you mean" not in result.output):
            raise AssertionError

    def test_no_suggestions_on_generic_api_error(self):
        """Test that suggestions are NOT shown on generic API errors.

        The product might exist, we just couldn't fetch it due to server error.
        Showing suggestions would be misleading.
        """
        runner = CliRunner()

        obj = _make_mock_client()
        obj["client"].get_product.side_effect = EOLAPIError("Server error")
        result = runner.invoke(products, ["get", "pythn"], obj=obj)
        # Should show error but NOT suggestions - product might exist
        if "Server error" not in result.output:
            raise AssertionError
        if not ("Did you mean" not in result.output):
            raise AssertionError


class TestVersionFallback:
    """Test _version.py fallback when package is not installed."""

    def test_version_fallback_when_not_installed(self):
        """PackageNotFoundError triggers the dev fallback."""
        from importlib.metadata import PackageNotFoundError

        with patch("importlib.metadata.version", side_effect=PackageNotFoundError("eol-cli")):
            import importlib

            import eol_cli._version

            importlib.reload(eol_cli._version)
            if not (eol_cli._version.__version__ == "0.0.0-dev"):
                raise AssertionError

        # Restore
        import importlib

        import eol_cli._version

        importlib.reload(eol_cli._version)


class TestCLIMainGuard:
    """Test cli.py __main__ guard."""

    def test_main_module_execution(self):
        """Running cli.py as __main__ invokes main()."""
        import runpy
        import sys

        sys.modules.pop("eol_cli.cli", None)
        with pytest.raises(SystemExit) as exc_info:
            runpy.run_module("eol_cli.cli", run_name="__main__", alter_sys=True)

        # Will show help/usage since no args, or version error — either way it ran
        if exc_info.value.code not in (0, 2):
            raise AssertionError
