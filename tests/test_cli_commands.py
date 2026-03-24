"""Tests for CLI commands"""

import json
import xml.etree.ElementTree as ET

import pytest
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
        runner = CliRunner()
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "EOL CLI" in result.output
        assert "Output Formats" in result.output

    def test_main_version(self):
        runner = CliRunner()
        result = runner.invoke(main, ["--version"])
        assert result.exit_code == 0
        assert "0.1.0" in result.output


@pytest.mark.api
class TestProductsCommands:
    """Test products commands."""

    def test_products_list(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(products, ["list"], obj=client_obj)
        assert result.exit_code == 0
        assert len(result.output) > 0

    def test_products_list_json(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(products, ["list", "--json"], obj=client_obj)
        assert result.exit_code == 0

        data = json.loads(result.output)
        assert "schema_version" in data
        assert "total" in data
        assert "result" in data

    def test_products_list_xml(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(products, ["list", "--xml"], obj=client_obj)
        assert result.exit_code == 0

        root = ET.fromstring(result.output)
        assert root.tag == "response"

    def test_products_list_json_xml_exclusive(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(products, ["list", "--json", "--xml"], obj=client_obj)
        assert result.exit_code == 2
        assert "mutually exclusive" in result.output

    def test_products_list_full(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(products, ["list", "--full"], obj=client_obj)
        assert result.exit_code == 0
        assert len(result.output) > 0

    def test_products_get_single(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(products, ["get", "python"], obj=client_obj)
        assert result.exit_code == 0
        assert len(result.output) > 0

    def test_products_get_single_all(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(products, ["get", "python", "--all"], obj=client_obj)
        assert result.exit_code == 0
        assert len(result.output) > 0

    def test_products_get_single_json(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(products, ["get", "python", "--json"], obj=client_obj)
        assert result.exit_code == 0

        data = json.loads(result.output)
        assert data["result"]["name"] == "python"

    def test_products_get_single_xml(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(products, ["get", "python", "--xml"], obj=client_obj)
        assert result.exit_code == 0

        root = ET.fromstring(result.output)
        assert root.tag == "response"

    def test_products_get_multiple(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(products, ["get", "python,nodejs"], obj=client_obj)
        assert result.exit_code == 0
        assert len(result.output) > 0
        assert "=" in result.output

    def test_products_get_multiple_json(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(products, ["get", "python,nodejs", "--json"], obj=client_obj)
        assert result.exit_code == 0

        data = json.loads(result.output)
        assert "total" in data
        assert data["total"] == 2
        assert "products" in data
        assert len(data["products"]) == 2

    def test_products_get_multiple_xml(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(products, ["get", "python,nodejs", "--xml"], obj=client_obj)
        assert result.exit_code == 0

        root = ET.fromstring(result.output)
        total = root.find("total")
        assert total.text == "2"

    def test_products_get_with_invalid_product(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(products, ["get", "nonexistent-product-xyz-123"], obj=client_obj)
        assert result.exit_code == 1
        assert "not found" in result.output.lower()

    def test_products_get_mixed_valid_invalid(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(products, ["get", "python,invalid-xyz,nodejs"], obj=client_obj)
        assert "Warning" in result.output
        assert "invalid-xyz" in result.output

    def test_products_release(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(products, ["release", "python", "3.11"], obj=client_obj)
        assert result.exit_code == 0
        assert len(result.output) > 0

    def test_products_release_latest(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(products, ["release", "python", "latest"], obj=client_obj)
        assert result.exit_code == 0
        assert len(result.output) > 0

    def test_products_release_json(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(products, ["release", "python", "latest", "--json"], obj=client_obj)
        assert result.exit_code == 0

        data = json.loads(result.output)
        assert "result" in data
        assert "name" in data["result"]

    def test_products_release_xml(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(products, ["release", "python", "latest", "--xml"], obj=client_obj)
        assert result.exit_code == 0

        root = ET.fromstring(result.output)
        assert root.tag == "response"

    def test_products_release_not_found(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(products, ["release", "python", "99.99"], obj=client_obj)
        assert result.exit_code == 1
        assert "not found" in result.output.lower()


@pytest.mark.api
class TestCategoriesCommands:
    """Test categories commands."""

    def test_categories_list(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(categories, ["list"], obj=client_obj)
        assert result.exit_code == 0
        assert len(result.output) > 0

    def test_categories_list_json(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(categories, ["list", "--json"], obj=client_obj)
        assert result.exit_code == 0

        data = json.loads(result.output)
        assert "total" in data
        assert "result" in data

    def test_categories_list_xml(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(categories, ["list", "--xml"], obj=client_obj)
        assert result.exit_code == 0

        root = ET.fromstring(result.output)
        assert root.tag == "response"

    def test_categories_get(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(categories, ["get", "os"], obj=client_obj)
        assert result.exit_code == 0
        assert len(result.output) > 0

    def test_categories_get_json(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(categories, ["get", "os", "--json"], obj=client_obj)
        assert result.exit_code == 0

        data = json.loads(result.output)
        assert "result" in data
        for product in data["result"]:
            assert product["category"] == "os"

    def test_categories_get_xml(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(categories, ["get", "os", "--xml"], obj=client_obj)
        assert result.exit_code == 0

        root = ET.fromstring(result.output)
        assert root.tag == "response"

    def test_categories_get_not_found(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(categories, ["get", "invalid-category-xyz"], obj=client_obj)
        assert result.exit_code == 1
        assert "not found" in result.output.lower()


@pytest.mark.api
class TestTagsCommands:
    """Test tags commands."""

    def test_tags_list(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(tags, ["list"], obj=client_obj)
        assert result.exit_code == 0
        assert len(result.output) > 0

    def test_tags_list_json(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(tags, ["list", "--json"], obj=client_obj)
        assert result.exit_code == 0

        data = json.loads(result.output)
        assert "total" in data
        assert "result" in data

    def test_tags_list_xml(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(tags, ["list", "--xml"], obj=client_obj)
        assert result.exit_code == 0

        root = ET.fromstring(result.output)
        assert root.tag == "response"

    def test_tags_get(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(tags, ["get", "linux-distribution"], obj=client_obj)
        assert result.exit_code == 0
        assert len(result.output) > 0

    def test_tags_get_json(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(tags, ["get", "linux-distribution", "--json"], obj=client_obj)
        assert result.exit_code == 0

        data = json.loads(result.output)
        assert "result" in data
        for product in data["result"]:
            assert "linux-distribution" in product["tags"]

    def test_tags_get_xml(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(tags, ["get", "linux-distribution", "--xml"], obj=client_obj)
        assert result.exit_code == 0

        root = ET.fromstring(result.output)
        assert root.tag == "response"

    def test_tags_get_not_found(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(tags, ["get", "invalid-tag-xyz-123"], obj=client_obj)
        assert result.exit_code == 1
        assert "not found" in result.output.lower()


@pytest.mark.api
class TestIdentifiersCommands:
    """Test identifiers commands."""

    def test_identifiers_list(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(identifiers, ["list"], obj=client_obj)
        assert result.exit_code == 0
        assert len(result.output) > 0

    def test_identifiers_list_json(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(identifiers, ["list", "--json"], obj=client_obj)
        assert result.exit_code == 0

        data = json.loads(result.output)
        assert "total" in data
        assert "result" in data

    def test_identifiers_list_xml(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(identifiers, ["list", "--xml"], obj=client_obj)
        assert result.exit_code == 0

        root = ET.fromstring(result.output)
        assert root.tag == "response"

    def test_identifiers_get(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(identifiers, ["get", "purl"], obj=client_obj)
        assert result.exit_code == 0
        assert len(result.output) > 0

    def test_identifiers_get_json(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(identifiers, ["get", "purl", "--json"], obj=client_obj)
        assert result.exit_code == 0

        data = json.loads(result.output)
        assert "result" in data
        assert len(data["result"]) > 0

    def test_identifiers_get_xml(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(identifiers, ["get", "purl", "--xml"], obj=client_obj)
        assert result.exit_code == 0

        root = ET.fromstring(result.output)
        assert root.tag == "response"

    def test_identifiers_get_not_found(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(identifiers, ["get", "invalid-type-xyz"], obj=client_obj)
        assert result.exit_code == 1
        assert "not found" in result.output.lower()


@pytest.mark.api
class TestIndexCommand:
    """Test index command."""

    def test_index(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(index, [], obj=client_obj)
        assert result.exit_code == 0
        assert len(result.output) > 0

    def test_index_json(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(index, ["--json"], obj=client_obj)
        assert result.exit_code == 0

        data = json.loads(result.output)
        assert "total" in data
        assert "result" in data

    def test_index_xml(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(index, ["--xml"], obj=client_obj)
        assert result.exit_code == 0

        root = ET.fromstring(result.output)
        assert root.tag == "response"
