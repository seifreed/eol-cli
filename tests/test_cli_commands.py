"""Tests for CLI commands"""

import json
import xml.etree.ElementTree as ET

from click.testing import CliRunner

from eol_cli.cli import main
from eol_cli.commands.categories import categories
from eol_cli.commands.identifiers import identifiers
from eol_cli.commands.index import index
from eol_cli.commands.products import products
from eol_cli.commands.tags import tags


class TestMainCLI:
    """Test main CLI entry point."""

    def test_main_help(self):
        """Test main --help command."""
        runner = CliRunner()
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "EOL CLI" in result.output
        assert "Output Formats" in result.output

    def test_main_version(self):
        """Test --version flag."""
        runner = CliRunner()
        result = runner.invoke(main, ["--version"])
        assert result.exit_code == 0
        assert "0.1.0" in result.output


class TestProductsCommands:
    """Test products commands."""

    def test_products_list(self):
        """Test products list command."""
        runner = CliRunner()
        result = runner.invoke(products, ["list"])
        assert result.exit_code == 0
        assert len(result.output) > 0

    def test_products_list_json(self):
        """Test products list with JSON output."""
        runner = CliRunner()
        result = runner.invoke(products, ["list", "--json"])
        assert result.exit_code == 0

        # Validate JSON
        data = json.loads(result.output)
        assert "schema_version" in data
        assert "total" in data
        assert "result" in data

    def test_products_list_xml(self):
        """Test products list with XML output."""
        runner = CliRunner()
        result = runner.invoke(products, ["list", "--xml"])
        assert result.exit_code == 0

        # Validate XML
        root = ET.fromstring(result.output)
        assert root.tag == "response"

    def test_products_list_json_xml_exclusive(self):
        """Test that --json and --xml are mutually exclusive."""
        runner = CliRunner()
        result = runner.invoke(products, ["list", "--json", "--xml"])
        assert result.exit_code == 1
        assert "mutually exclusive" in result.output

    def test_products_list_full(self):
        """Test products list --full command."""
        runner = CliRunner()
        result = runner.invoke(products, ["list", "--full"])
        assert result.exit_code == 0
        assert len(result.output) > 0

    def test_products_get_single(self):
        """Test products get with single product."""
        runner = CliRunner()
        result = runner.invoke(products, ["get", "python"])
        assert result.exit_code == 0
        assert len(result.output) > 0

    def test_products_get_single_all(self):
        """Test products get with --all flag."""
        runner = CliRunner()
        result = runner.invoke(products, ["get", "python", "--all"])
        assert result.exit_code == 0
        assert len(result.output) > 0

    def test_products_get_single_json(self):
        """Test products get with JSON output."""
        runner = CliRunner()
        result = runner.invoke(products, ["get", "python", "--json"])
        assert result.exit_code == 0

        data = json.loads(result.output)
        assert data["result"]["name"] == "python"

    def test_products_get_single_xml(self):
        """Test products get with XML output."""
        runner = CliRunner()
        result = runner.invoke(products, ["get", "python", "--xml"])
        assert result.exit_code == 0

        root = ET.fromstring(result.output)
        assert root.tag == "response"

    def test_products_get_multiple(self):
        """Test products get with multiple products."""
        runner = CliRunner()
        result = runner.invoke(products, ["get", "python,nodejs"])
        assert result.exit_code == 0
        assert len(result.output) > 0
        # Should have separator between products
        assert "=" in result.output

    def test_products_get_multiple_json(self):
        """Test products get multiple with JSON output."""
        runner = CliRunner()
        result = runner.invoke(products, ["get", "python,nodejs", "--json"])
        assert result.exit_code == 0

        data = json.loads(result.output)
        assert "total" in data
        assert data["total"] == 2
        assert "products" in data
        assert len(data["products"]) == 2

    def test_products_get_multiple_xml(self):
        """Test products get multiple with XML output."""
        runner = CliRunner()
        result = runner.invoke(products, ["get", "python,nodejs", "--xml"])
        assert result.exit_code == 0

        root = ET.fromstring(result.output)
        total = root.find("total")
        assert total.text == "2"

    def test_products_get_with_invalid_product(self):
        """Test products get with invalid product."""
        runner = CliRunner()
        result = runner.invoke(products, ["get", "nonexistent-product-xyz-123"])
        assert result.exit_code == 1
        assert "not found" in result.output.lower()

    def test_products_get_mixed_valid_invalid(self):
        """Test products get with mix of valid and invalid products."""
        runner = CliRunner()
        result = runner.invoke(products, ["get", "python,invalid-xyz,nodejs"])
        # Should show warning but continue with valid products
        assert "Warning" in result.output
        assert "invalid-xyz" in result.output

    def test_products_release(self):
        """Test products release command."""
        runner = CliRunner()
        result = runner.invoke(products, ["release", "python", "3.11"])
        assert result.exit_code == 0
        assert len(result.output) > 0

    def test_products_release_latest(self):
        """Test products release latest."""
        runner = CliRunner()
        result = runner.invoke(products, ["release", "python", "latest"])
        assert result.exit_code == 0
        assert len(result.output) > 0

    def test_products_release_json(self):
        """Test products release with JSON output."""
        runner = CliRunner()
        result = runner.invoke(products, ["release", "python", "latest", "--json"])
        assert result.exit_code == 0

        data = json.loads(result.output)
        assert "result" in data
        assert "name" in data["result"]

    def test_products_release_xml(self):
        """Test products release with XML output."""
        runner = CliRunner()
        result = runner.invoke(products, ["release", "python", "latest", "--xml"])
        assert result.exit_code == 0

        root = ET.fromstring(result.output)
        assert root.tag == "response"

    def test_products_release_not_found(self):
        """Test products release with invalid release."""
        runner = CliRunner()
        result = runner.invoke(products, ["release", "python", "99.99"])
        assert result.exit_code == 1
        assert "not found" in result.output.lower()


class TestCategoriesCommands:
    """Test categories commands."""

    def test_categories_list(self):
        """Test categories list command."""
        runner = CliRunner()
        result = runner.invoke(categories, ["list"])
        assert result.exit_code == 0
        assert len(result.output) > 0

    def test_categories_list_json(self):
        """Test categories list with JSON output."""
        runner = CliRunner()
        result = runner.invoke(categories, ["list", "--json"])
        assert result.exit_code == 0

        data = json.loads(result.output)
        assert "total" in data
        assert "result" in data

    def test_categories_list_xml(self):
        """Test categories list with XML output."""
        runner = CliRunner()
        result = runner.invoke(categories, ["list", "--xml"])
        assert result.exit_code == 0

        root = ET.fromstring(result.output)
        assert root.tag == "response"

    def test_categories_get(self):
        """Test categories get command."""
        runner = CliRunner()
        result = runner.invoke(categories, ["get", "os"])
        assert result.exit_code == 0
        assert len(result.output) > 0

    def test_categories_get_json(self):
        """Test categories get with JSON output."""
        runner = CliRunner()
        result = runner.invoke(categories, ["get", "os", "--json"])
        assert result.exit_code == 0

        data = json.loads(result.output)
        assert "result" in data
        # All products should be in 'os' category
        for product in data["result"]:
            assert product["category"] == "os"

    def test_categories_get_xml(self):
        """Test categories get with XML output."""
        runner = CliRunner()
        result = runner.invoke(categories, ["get", "os", "--xml"])
        assert result.exit_code == 0

        root = ET.fromstring(result.output)
        assert root.tag == "response"

    def test_categories_get_not_found(self):
        """Test categories get with invalid category."""
        runner = CliRunner()
        result = runner.invoke(categories, ["get", "invalid-category-xyz"])
        assert result.exit_code == 1
        assert "not found" in result.output.lower()


class TestTagsCommands:
    """Test tags commands."""

    def test_tags_list(self):
        """Test tags list command."""
        runner = CliRunner()
        result = runner.invoke(tags, ["list"])
        assert result.exit_code == 0
        assert len(result.output) > 0

    def test_tags_list_json(self):
        """Test tags list with JSON output."""
        runner = CliRunner()
        result = runner.invoke(tags, ["list", "--json"])
        assert result.exit_code == 0

        data = json.loads(result.output)
        assert "total" in data
        assert "result" in data

    def test_tags_list_xml(self):
        """Test tags list with XML output."""
        runner = CliRunner()
        result = runner.invoke(tags, ["list", "--xml"])
        assert result.exit_code == 0

        root = ET.fromstring(result.output)
        assert root.tag == "response"

    def test_tags_get(self):
        """Test tags get command."""
        runner = CliRunner()
        result = runner.invoke(tags, ["get", "linux-distribution"])
        assert result.exit_code == 0
        assert len(result.output) > 0

    def test_tags_get_json(self):
        """Test tags get with JSON output."""
        runner = CliRunner()
        result = runner.invoke(tags, ["get", "linux-distribution", "--json"])
        assert result.exit_code == 0

        data = json.loads(result.output)
        assert "result" in data
        # All products should have the tag
        for product in data["result"]:
            assert "linux-distribution" in product["tags"]

    def test_tags_get_xml(self):
        """Test tags get with XML output."""
        runner = CliRunner()
        result = runner.invoke(tags, ["get", "linux-distribution", "--xml"])
        assert result.exit_code == 0

        root = ET.fromstring(result.output)
        assert root.tag == "response"

    def test_tags_get_not_found(self):
        """Test tags get with invalid tag."""
        runner = CliRunner()
        result = runner.invoke(tags, ["get", "invalid-tag-xyz-123"])
        assert result.exit_code == 1
        assert "not found" in result.output.lower()


class TestIdentifiersCommands:
    """Test identifiers commands."""

    def test_identifiers_list(self):
        """Test identifiers list command."""
        runner = CliRunner()
        result = runner.invoke(identifiers, ["list"])
        assert result.exit_code == 0
        assert len(result.output) > 0

    def test_identifiers_list_json(self):
        """Test identifiers list with JSON output."""
        runner = CliRunner()
        result = runner.invoke(identifiers, ["list", "--json"])
        assert result.exit_code == 0

        data = json.loads(result.output)
        assert "total" in data
        assert "result" in data

    def test_identifiers_list_xml(self):
        """Test identifiers list with XML output."""
        runner = CliRunner()
        result = runner.invoke(identifiers, ["list", "--xml"])
        assert result.exit_code == 0

        root = ET.fromstring(result.output)
        assert root.tag == "response"

    def test_identifiers_get(self):
        """Test identifiers get command."""
        runner = CliRunner()
        result = runner.invoke(identifiers, ["get", "purl"])
        assert result.exit_code == 0
        assert len(result.output) > 0

    def test_identifiers_get_json(self):
        """Test identifiers get with JSON output."""
        runner = CliRunner()
        result = runner.invoke(identifiers, ["get", "purl", "--json"])
        assert result.exit_code == 0

        data = json.loads(result.output)
        assert "result" in data
        assert len(data["result"]) > 0

    def test_identifiers_get_xml(self):
        """Test identifiers get with XML output."""
        runner = CliRunner()
        result = runner.invoke(identifiers, ["get", "purl", "--xml"])
        assert result.exit_code == 0

        root = ET.fromstring(result.output)
        assert root.tag == "response"

    def test_identifiers_get_not_found(self):
        """Test identifiers get with invalid type."""
        runner = CliRunner()
        result = runner.invoke(identifiers, ["get", "invalid-type-xyz"])
        assert result.exit_code == 1
        assert "not found" in result.output.lower()


class TestIndexCommand:
    """Test index command."""

    def test_index(self):
        """Test index command."""
        runner = CliRunner()
        result = runner.invoke(index, [])
        assert result.exit_code == 0
        assert len(result.output) > 0

    def test_index_json(self):
        """Test index with JSON output."""
        runner = CliRunner()
        result = runner.invoke(index, ["--json"])
        assert result.exit_code == 0

        data = json.loads(result.output)
        assert "total" in data
        assert "result" in data

    def test_index_xml(self):
        """Test index with XML output."""
        runner = CliRunner()
        result = runner.invoke(index, ["--xml"])
        assert result.exit_code == 0

        root = ET.fromstring(result.output)
        assert root.tag == "response"
