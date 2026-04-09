"""Tests for Rich formatter edge cases including empty data, optional fields, and complex scenarios."""

import pytest
from click.testing import CliRunner

from eol_cli.api.client import EOLClient
from eol_cli.commands.categories import categories
from eol_cli.commands.identifiers import identifiers
from eol_cli.commands.products import products
from eol_cli.commands.tags import tags
from eol_cli.formatters import rich_formatter


class TestRichFormatterEmptyCases:
    """Test rich formatter with empty/no data cases."""

    def test_format_product_details_empty_result(self, make_console):
        data = {"result": {}}
        buf, c = make_console()
        rich_formatter.format_product_details(data, show_all=False, console=c)
        if "No data found" not in buf.getvalue():
            raise AssertionError

    def test_format_product_details_no_releases_prints_notice(self, make_console):
        data = {"result": {"name": "test-product", "label": "Test Product", "releases": []}}
        buf, c = make_console()
        rich_formatter.format_product_details(data, show_all=False, console=c)
        if "No release cycles found" not in buf.getvalue():
            raise AssertionError

    def test_format_release_details_empty_result(self, make_console):
        data = {"result": {}}
        buf, c = make_console()
        rich_formatter.format_release_details(data, console=c)
        if "No data found" not in buf.getvalue():
            raise AssertionError

    def test_format_product_list_empty_result(self, make_console):
        data = {"result": [], "total": 0}
        buf, c = make_console()
        rich_formatter.format_product_list(data, full=False, console=c)
        if "No products found" not in buf.getvalue():
            raise AssertionError

    def test_format_identifier_list_empty_result(self, make_console):
        data = {"result": [], "total": 0}
        buf, c = make_console()
        rich_formatter.format_identifier_list(data, console=c)
        if "No identifiers found" not in buf.getvalue():
            raise AssertionError


class TestRichFormatterLatestVersionDict:
    """Test rich formatter with latest version as dict."""

    def test_format_product_details_latest_dict(self, make_console):
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

        buf, c = make_console()
        rich_formatter.format_product_details(data, show_all=False, console=c)
        if "1.0.5" not in buf.getvalue():
            raise AssertionError


class TestRichFormatterOptionalFields:
    """Test rich formatter with optional fields present."""

    def test_format_release_details_with_codename(self, make_console):
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
        buf, c = make_console()
        rich_formatter.format_release_details(data, console=c)
        if "Jammy Jellyfish" not in buf.getvalue():
            raise AssertionError

    def test_format_release_details_with_lts_from(self, make_console):
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
        buf, c = make_console()
        rich_formatter.format_release_details(data, console=c)
        if "2024-06-01" not in buf.getvalue():
            raise AssertionError

    def test_format_release_details_with_eoes(self, make_console):
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
        buf, c = make_console()
        rich_formatter.format_release_details(data, console=c)
        if "2026-01-01" not in buf.getvalue():
            raise AssertionError

    def test_format_release_details_with_discontinued(self, make_console):
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
        buf, c = make_console()
        rich_formatter.format_release_details(data, console=c)
        if "2023-06-01" not in buf.getvalue():
            raise AssertionError


class TestRichFormatterDateEdgeCases:
    """Test date formatting edge cases."""

    def test_format_date_with_invalid_format(self):
        result = rich_formatter._format_date("not-a-date")
        if "not-a-date" not in result:
            raise AssertionError

    def test_format_date_with_empty_string(self):
        result = rich_formatter._format_date("")
        if not (result is not None):
            raise AssertionError


class TestRichFormatterEOLStatus:
    """Test EOL status formatting edge cases."""

    def test_format_eol_status_eol_with_date(self):
        """Test EOL status when product is EOL with a date."""
        result = rich_formatter._format_eol_status(True, "2020-01-01")
        if "EOL" not in result:
            raise AssertionError
        if "2020-01-01" not in result:
            raise AssertionError

    def test_format_eol_status_eol_without_date(self):
        """Test EOL status when product is EOL but no date provided."""
        result = rich_formatter._format_eol_status(True, None)
        if "EOL" not in result:
            raise AssertionError
        # Simplified output: EOL without date shows just "[red]EOL[/red]"
        if not ("[red]EOL[/red]" == result):
            raise AssertionError

    def test_format_eol_status_active_with_date(self):
        """Test EOL status when product is active with EOL date."""
        result = rich_formatter._format_eol_status(False, "2030-01-01")
        if "Active" not in result:
            raise AssertionError
        if "EOL: 2030-01-01" not in result:
            raise AssertionError

    def test_format_eol_status_active_without_date(self):
        """Test EOL status when product is active but no EOL date scheduled."""
        result = rich_formatter._format_eol_status(False, None)
        if "Active" not in result:
            raise AssertionError
        if "no EOL date scheduled" not in result:
            raise AssertionError


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
        """Whitespace around commas is stripped — behaves as 'python,nodejs'."""
        runner = CliRunner()
        result = runner.invoke(products, ["get", " python , nodejs "], obj=client_obj)
        if not (result.exit_code == 0):
            raise AssertionError

    def test_categories_get_with_valid_category(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(categories, ["get", "os"], obj=client_obj)
        if not (result.exit_code == 0):
            raise AssertionError

    def test_tags_get_with_valid_tag(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(tags, ["get", "linux-distribution"], obj=client_obj)
        if not (result.exit_code == 0):
            raise AssertionError

    def test_identifiers_get_with_valid_type(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(identifiers, ["get", "purl"], obj=client_obj)
        if not (result.exit_code == 0):
            raise AssertionError


@pytest.mark.api
class TestProductsCommandEdgeCases:
    """Test products command edge cases."""

    def test_products_get_multiple_with_one_valid_one_invalid(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(products, ["get", "python,invalid-product-xyz"], obj=client_obj)
        if not ("python" in result.output.lower() or "warning" in result.output.lower()):
            raise AssertionError

    def test_products_release_invalid_in_json_mode(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(
            products, ["release", "invalid-xyz", "latest", "--json"], obj=client_obj
        )
        if not (result.exit_code == 1):
            raise AssertionError


@pytest.mark.api
class TestAPIClientLinesCoverage:
    """Test API client error paths with real requests."""

    def test_not_found_error_raises_for_unknown_product(self):
        from eol_cli.api.client import EOLNotFoundError

        with EOLClient() as client:
            with pytest.raises(EOLNotFoundError):
                client.get_product("this-absolutely-does-not-exist-xyz-123-456")


class TestCLIMainFunction:
    """Test main CLI function edge case."""

    def test_cli_invalid_command(self):
        from eol_cli.cli import main

        runner = CliRunner()
        result = runner.invoke(main, ["invalid-command"])
        if not (result.exit_code != 0):
            raise AssertionError


@pytest.mark.api
class TestFormatterComplexScenarios:
    """Test complex formatter scenarios for remaining lines."""

    def test_product_with_real_data_show_all_false(self, make_console):
        with EOLClient() as client:
            data = client.get_product("ubuntu")
            buf, c = make_console()
            rich_formatter.format_product_details(data, show_all=False, console=c)
            if not (len(buf.getvalue()) > 0):
                raise AssertionError

    def test_product_with_empty_links_and_identifiers(self, make_console):
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
        buf, c = make_console()
        rich_formatter.format_product_details(data, show_all=True, console=c)
        if "Test" not in buf.getvalue():
            raise AssertionError
