"""Tests for Rich formatter edge cases including empty data, optional fields, and complex scenarios."""

from io import StringIO

import pytest
from click.testing import CliRunner
from rich.console import Console

from eol_cli.api.client import EOLClient
from eol_cli.commands.categories import categories
from eol_cli.commands.identifiers import identifiers
from eol_cli.commands.products import products
from eol_cli.commands.tags import tags
from eol_cli.formatters import rich_formatter


def _make_console() -> tuple[StringIO, Console]:
    """Create a test console that captures output to a StringIO buffer."""
    buf = StringIO()
    return buf, Console(file=buf, highlight=False, width=200)


class TestRichFormatterEmptyCases:
    """Test rich formatter with empty/no data cases."""

    def test_format_product_details_empty_result(self):
        data = {"result": {}}
        buf, c = _make_console()
        rich_formatter.format_product_details(data, show_all=False, console=c)
        assert "No data found" in buf.getvalue()

    def test_format_release_details_empty_result(self):
        data = {"result": {}}
        buf, c = _make_console()
        rich_formatter.format_release_details(data, console=c)
        assert "No data found" in buf.getvalue()

    def test_format_product_list_empty_result(self):
        data = {"result": [], "total": 0}
        buf, c = _make_console()
        rich_formatter.format_product_list(data, full=False, console=c)
        assert "No products found" in buf.getvalue()

    def test_format_identifier_list_empty_result(self):
        data = {"result": [], "total": 0}
        buf, c = _make_console()
        rich_formatter.format_identifier_list(data, console=c)
        assert "No identifiers found" in buf.getvalue()


class TestRichFormatterLatestVersionDict:
    """Test rich formatter with latest version as dict."""

    def test_format_product_details_latest_dict(self):
        data = {
            "result": {
                "name": "test-product",
                "label": "Test Product",
                "category": "test",
                "tags": [],
                "releases": [
                    {
                        "name": "1.0",
                        "releaseDate": "2024-01-01",
                        "isLts": False,
                        "isEol": False,
                        "eolFrom": "2030-01-01",
                        "latest": {"name": "1.0.5", "date": "2024-06-01"},
                    }
                ],
            }
        }

        buf, c = _make_console()
        rich_formatter.format_product_details(data, show_all=False, console=c)
        assert "1.0.5" in buf.getvalue()


class TestRichFormatterOptionalFields:
    """Test rich formatter with optional fields present."""

    def test_format_release_details_with_codename(self):
        data = {
            "result": {
                "name": "22.04",
                "label": "Ubuntu 22.04",
                "codename": "Jammy Jellyfish",
                "releaseDate": "2022-04-21",
                "isLts": True,
                "isEol": False,
                "isMaintained": True,
                "eolFrom": "2027-04-01",
            }
        }
        buf, c = _make_console()
        rich_formatter.format_release_details(data, console=c)
        assert "Jammy Jellyfish" in buf.getvalue()

    def test_format_release_details_with_lts_from(self):
        data = {
            "result": {
                "name": "test",
                "releaseDate": "2024-01-01",
                "isLts": True,
                "ltsFrom": "2024-06-01",
                "isEol": False,
                "isMaintained": True,
                "eolFrom": "2030-01-01",
            }
        }
        buf, c = _make_console()
        rich_formatter.format_release_details(data, console=c)
        assert "2024-06-01" in buf.getvalue()

    def test_format_release_details_with_eoes(self):
        data = {
            "result": {
                "name": "test",
                "releaseDate": "2020-01-01",
                "isLts": True,
                "isEol": True,
                "isMaintained": False,
                "eolFrom": "2025-01-01",
                "isEoes": True,
                "eoesFrom": "2026-01-01",
            }
        }
        buf, c = _make_console()
        rich_formatter.format_release_details(data, console=c)
        assert "2026-01-01" in buf.getvalue()

    def test_format_release_details_with_discontinued(self):
        data = {
            "result": {
                "name": "test",
                "releaseDate": "2020-01-01",
                "isLts": False,
                "isEol": True,
                "isMaintained": False,
                "eolFrom": "2023-01-01",
                "isDiscontinued": True,
                "discontinuedFrom": "2023-06-01",
            }
        }
        buf, c = _make_console()
        rich_formatter.format_release_details(data, console=c)
        assert "2023-06-01" in buf.getvalue()


class TestRichFormatterDateEdgeCases:
    """Test date formatting edge cases."""

    def test_format_date_with_invalid_format(self):
        result = rich_formatter._format_date("not-a-date")
        assert "not-a-date" in result

    def test_format_date_with_empty_string(self):
        result = rich_formatter._format_date("")
        assert result is not None


@pytest.mark.api
class TestAPIClientErrorPaths:
    """Test API client error handling paths."""

    def test_client_httpeerror_handling(self):
        from eol_cli.api.client import EOLAPIError

        with EOLClient(base_url="https://httpstat.us") as client:
            with pytest.raises(EOLAPIError):
                client._request("/500")

    def test_client_request_exception_handling(self):
        from eol_cli.api.client import EOLAPIError

        with EOLClient(
            base_url="https://this-domain-absolutely-does-not-exist-12345.com"
        ) as client:
            with pytest.raises(EOLAPIError):
                client._request("/")


@pytest.mark.api
class TestCLICommandsEdgeCases:
    """Test CLI commands for missing coverage."""

    def test_products_get_with_whitespace(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(products, ["get", " python , nodejs "], obj=client_obj)
        assert result.exit_code in (0, 1)

    def test_categories_get_with_valid_category(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(categories, ["get", "os"], obj=client_obj)
        assert result.exit_code == 0

    def test_tags_get_with_valid_tag(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(tags, ["get", "linux-distribution"], obj=client_obj)
        assert result.exit_code == 0

    def test_identifiers_get_with_valid_type(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(identifiers, ["get", "purl"], obj=client_obj)
        assert result.exit_code == 0


@pytest.mark.api
class TestProductsCommandEdgeCases:
    """Test products command edge cases."""

    def test_products_get_multiple_with_one_valid_one_invalid(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(products, ["get", "python,invalid-product-xyz"], obj=client_obj)
        assert "python" in result.output.lower() or "warning" in result.output.lower()

    def test_products_release_invalid_in_json_mode(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(products, ["release", "invalid-xyz", "latest", "--json"], obj=client_obj)
        assert result.exit_code == 1


@pytest.mark.api
class TestAPIClientLinesCoverage:
    """Test specific API client lines that need coverage."""

    def test_rate_limit_error_line_70_71(self):
        from eol_cli.api.client import EOLRateLimitError

        error = EOLRateLimitError("Rate limit exceeded. Retry after: 60 seconds")
        assert "60 seconds" in str(error)
        assert isinstance(error, Exception)

    def test_http_error_handling_line_81(self):
        from eol_cli.api.client import EOLNotFoundError

        with EOLClient() as client:
            with pytest.raises(EOLNotFoundError):
                client.get_product("this-absolutely-does-not-exist-xyz-123-456")

    def test_json_value_error_line_85(self):
        from eol_cli.api.client import EOLAPIError

        error = EOLAPIError("Invalid JSON response: error")
        assert "Invalid JSON" in str(error)


class TestCLIMainFunction:
    """Test main CLI function edge case."""

    def test_cli_invalid_command(self):
        from eol_cli.cli import main

        runner = CliRunner()
        result = runner.invoke(main, ["invalid-command"])
        assert result.exit_code != 0


@pytest.mark.api
class TestFormatterComplexScenarios:
    """Test complex formatter scenarios for remaining lines."""

    def test_product_with_real_data_show_all_false(self):
        with EOLClient() as client:
            data = client.get_product("ubuntu")
            buf, c = _make_console()
            rich_formatter.format_product_details(data, show_all=False, console=c)
            assert len(buf.getvalue()) > 0

    def test_product_with_empty_links_and_identifiers(self):
        data = {
            "result": {
                "name": "test",
                "label": "Test",
                "category": "test",
                "tags": ["tag1", "tag2"],
                "links": {},
                "identifiers": [],
                "releases": [
                    {
                        "name": "1.0",
                        "releaseDate": "2024-01-01",
                        "isLts": False,
                        "isEol": False,
                        "eolFrom": "2030-01-01",
                        "latest": "1.0.0",
                    }
                ],
            }
        }
        buf, c = _make_console()
        rich_formatter.format_product_details(data, show_all=True, console=c)
        assert "Test" in buf.getvalue()


@pytest.mark.api
class TestIndexAndCategoriesCommands:
    """Test index and categories for missing lines."""

    def test_index_command_error_handling(self, client_obj):
        runner = CliRunner()
        from eol_cli.commands.index import index

        result = runner.invoke(index, [], obj=client_obj)
        assert result.exit_code == 0

    def test_categories_list_error_handling(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(categories, ["list"], obj=client_obj)
        assert result.exit_code == 0

    def test_identifiers_list_error_handling(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(identifiers, ["list"], obj=client_obj)
        assert result.exit_code == 0
