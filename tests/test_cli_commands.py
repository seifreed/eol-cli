"""Tests for CLI commands"""

import json

import pytest
from click.testing import CliRunner
from defusedxml import ElementTree as ET

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
        if not (result.exit_code == 0):
            raise AssertionError
        if "EOL CLI" not in result.output:
            raise AssertionError
        if "Output Formats" not in result.output:
            raise AssertionError

    def test_main_version(self):
        runner = CliRunner()
        result = runner.invoke(main, ["--version"])
        if not (result.exit_code == 0):
            raise AssertionError
        if not result.output.startswith("eol-cli, version "):
            raise AssertionError


@pytest.mark.api
class TestProductsCommands:
    """Test products commands."""

    def test_products_list(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(products, ["list"], obj=client_obj)
        if not (result.exit_code == 0):
            raise AssertionError
        if not (len(result.output) > 0):
            raise AssertionError

    def test_products_list_json(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(products, ["list", "--json"], obj=client_obj)
        if not (result.exit_code == 0):
            raise AssertionError

        data = json.loads(result.output)
        if "schema_version" not in data:
            raise AssertionError
        if "total" not in data:
            raise AssertionError
        if "result" not in data:
            raise AssertionError

    def test_products_list_xml(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(products, ["list", "--xml"], obj=client_obj)
        if not (result.exit_code == 0):
            raise AssertionError

        root = ET.fromstring(result.output)
        if not (root.tag == "response"):
            raise AssertionError

    def test_products_list_json_xml_exclusive(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(products, ["list", "--json", "--xml"], obj=client_obj)
        if not (result.exit_code == 2):
            raise AssertionError
        if "mutually exclusive" not in result.output:
            raise AssertionError

    def test_products_list_full(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(products, ["list", "--full"], obj=client_obj)
        if not (result.exit_code == 0):
            raise AssertionError
        if not (len(result.output) > 0):
            raise AssertionError

    def test_products_get_single(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(products, ["get", "python"], obj=client_obj)
        if not (result.exit_code == 0):
            raise AssertionError
        if not (len(result.output) > 0):
            raise AssertionError

    def test_products_get_single_all(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(products, ["get", "python", "--all"], obj=client_obj)
        if not (result.exit_code == 0):
            raise AssertionError
        if not (len(result.output) > 0):
            raise AssertionError

    def test_products_get_single_json(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(products, ["get", "python", "--json"], obj=client_obj)
        if not (result.exit_code == 0):
            raise AssertionError

        data = json.loads(result.output)
        if not (data["result"]["name"] == "python"):
            raise AssertionError

    def test_products_get_single_xml(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(products, ["get", "python", "--xml"], obj=client_obj)
        if not (result.exit_code == 0):
            raise AssertionError

        root = ET.fromstring(result.output)
        if not (root.tag == "response"):
            raise AssertionError

    def test_products_get_multiple(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(products, ["get", "python,nodejs"], obj=client_obj)
        if not (result.exit_code == 0):
            raise AssertionError
        if not (len(result.output) > 0):
            raise AssertionError
        if "=" not in result.output:
            raise AssertionError

    def test_products_get_multiple_json(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(products, ["get", "python,nodejs", "--json"], obj=client_obj)
        if not (result.exit_code == 0):
            raise AssertionError

        data = json.loads(result.output)
        if "total" not in data:
            raise AssertionError
        if not (data["total"] == 2):
            raise AssertionError
        if "products" not in data:
            raise AssertionError
        if not (len(data["products"]) == 2):
            raise AssertionError

    def test_products_get_multiple_xml(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(products, ["get", "python,nodejs", "--xml"], obj=client_obj)
        if not (result.exit_code == 0):
            raise AssertionError

        root = ET.fromstring(result.output)
        total = root.find("total")
        if not (total.text == "2"):
            raise AssertionError

    def test_products_get_with_invalid_product(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(products, ["get", "nonexistent-product-xyz-123"], obj=client_obj)
        if not (result.exit_code == 1):
            raise AssertionError
        if "not found" not in result.output.lower():
            raise AssertionError

    def test_products_get_mixed_valid_invalid(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(products, ["get", "python,invalid-xyz,nodejs"], obj=client_obj)
        if "Warning" not in result.output:
            raise AssertionError
        if "invalid-xyz" not in result.output:
            raise AssertionError

    def test_products_release(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(products, ["release", "python", "3.11"], obj=client_obj)
        if not (result.exit_code == 0):
            raise AssertionError
        if not (len(result.output) > 0):
            raise AssertionError

    def test_products_release_latest(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(products, ["release", "python", "latest"], obj=client_obj)
        if not (result.exit_code == 0):
            raise AssertionError
        if not (len(result.output) > 0):
            raise AssertionError

    def test_products_release_json(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(products, ["release", "python", "latest", "--json"], obj=client_obj)
        if not (result.exit_code == 0):
            raise AssertionError

        data = json.loads(result.output)
        if "result" not in data:
            raise AssertionError
        if "name" not in data["result"]:
            raise AssertionError

    def test_products_release_xml(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(products, ["release", "python", "latest", "--xml"], obj=client_obj)
        if not (result.exit_code == 0):
            raise AssertionError

        root = ET.fromstring(result.output)
        if not (root.tag == "response"):
            raise AssertionError

    def test_products_release_not_found(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(products, ["release", "python", "99.99"], obj=client_obj)
        if not (result.exit_code == 1):
            raise AssertionError
        if "not found" not in result.output.lower():
            raise AssertionError


@pytest.mark.api
class TestCategoriesCommands:
    """Test categories commands."""

    def test_categories_list(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(categories, ["list"], obj=client_obj)
        if not (result.exit_code == 0):
            raise AssertionError
        if not (len(result.output) > 0):
            raise AssertionError

    def test_categories_list_json(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(categories, ["list", "--json"], obj=client_obj)
        if not (result.exit_code == 0):
            raise AssertionError

        data = json.loads(result.output)
        if "total" not in data:
            raise AssertionError
        if "result" not in data:
            raise AssertionError

    def test_categories_list_xml(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(categories, ["list", "--xml"], obj=client_obj)
        if not (result.exit_code == 0):
            raise AssertionError

        root = ET.fromstring(result.output)
        if not (root.tag == "response"):
            raise AssertionError

    def test_categories_get(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(categories, ["get", "os"], obj=client_obj)
        if not (result.exit_code == 0):
            raise AssertionError
        if not (len(result.output) > 0):
            raise AssertionError

    def test_categories_get_json(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(categories, ["get", "os", "--json"], obj=client_obj)
        if not (result.exit_code == 0):
            raise AssertionError

        data = json.loads(result.output)
        if "result" not in data:
            raise AssertionError
        for product in data["result"]:
            if not (product["category"] == "os"):
                raise AssertionError

    def test_categories_get_xml(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(categories, ["get", "os", "--xml"], obj=client_obj)
        if not (result.exit_code == 0):
            raise AssertionError

        root = ET.fromstring(result.output)
        if not (root.tag == "response"):
            raise AssertionError

    def test_categories_get_not_found(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(categories, ["get", "invalid-category-xyz"], obj=client_obj)
        if not (result.exit_code == 1):
            raise AssertionError
        if "not found" not in result.output.lower():
            raise AssertionError


@pytest.mark.api
class TestTagsCommands:
    """Test tags commands."""

    def test_tags_list(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(tags, ["list"], obj=client_obj)
        if not (result.exit_code == 0):
            raise AssertionError
        if not (len(result.output) > 0):
            raise AssertionError

    def test_tags_list_json(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(tags, ["list", "--json"], obj=client_obj)
        if not (result.exit_code == 0):
            raise AssertionError

        data = json.loads(result.output)
        if "total" not in data:
            raise AssertionError
        if "result" not in data:
            raise AssertionError

    def test_tags_list_xml(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(tags, ["list", "--xml"], obj=client_obj)
        if not (result.exit_code == 0):
            raise AssertionError

        root = ET.fromstring(result.output)
        if not (root.tag == "response"):
            raise AssertionError

    def test_tags_get(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(tags, ["get", "linux-distribution"], obj=client_obj)
        if not (result.exit_code == 0):
            raise AssertionError
        if not (len(result.output) > 0):
            raise AssertionError

    def test_tags_get_json(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(tags, ["get", "linux-distribution", "--json"], obj=client_obj)
        if not (result.exit_code == 0):
            raise AssertionError

        data = json.loads(result.output)
        if "result" not in data:
            raise AssertionError
        for product in data["result"]:
            if "linux-distribution" not in product["tags"]:
                raise AssertionError

    def test_tags_get_xml(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(tags, ["get", "linux-distribution", "--xml"], obj=client_obj)
        if not (result.exit_code == 0):
            raise AssertionError

        root = ET.fromstring(result.output)
        if not (root.tag == "response"):
            raise AssertionError

    def test_tags_get_not_found(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(tags, ["get", "invalid-tag-xyz-123"], obj=client_obj)
        if not (result.exit_code == 1):
            raise AssertionError
        if "not found" not in result.output.lower():
            raise AssertionError


@pytest.mark.api
class TestIdentifiersCommands:
    """Test identifiers commands."""

    def test_identifiers_list(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(identifiers, ["list"], obj=client_obj)
        if not (result.exit_code == 0):
            raise AssertionError
        if not (len(result.output) > 0):
            raise AssertionError

    def test_identifiers_list_json(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(identifiers, ["list", "--json"], obj=client_obj)
        if not (result.exit_code == 0):
            raise AssertionError

        data = json.loads(result.output)
        if "total" not in data:
            raise AssertionError
        if "result" not in data:
            raise AssertionError

    def test_identifiers_list_xml(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(identifiers, ["list", "--xml"], obj=client_obj)
        if not (result.exit_code == 0):
            raise AssertionError

        root = ET.fromstring(result.output)
        if not (root.tag == "response"):
            raise AssertionError

    def test_identifiers_get(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(identifiers, ["get", "purl"], obj=client_obj)
        if not (result.exit_code == 0):
            raise AssertionError
        if not (len(result.output) > 0):
            raise AssertionError

    def test_identifiers_get_json(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(identifiers, ["get", "purl", "--json"], obj=client_obj)
        if not (result.exit_code == 0):
            raise AssertionError

        data = json.loads(result.output)
        if "result" not in data:
            raise AssertionError
        if not (len(data["result"]) > 0):
            raise AssertionError

    def test_identifiers_get_xml(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(identifiers, ["get", "purl", "--xml"], obj=client_obj)
        if not (result.exit_code == 0):
            raise AssertionError

        root = ET.fromstring(result.output)
        if not (root.tag == "response"):
            raise AssertionError

    def test_identifiers_get_not_found(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(identifiers, ["get", "invalid-type-xyz"], obj=client_obj)
        if not (result.exit_code == 1):
            raise AssertionError
        if "not found" not in result.output.lower():
            raise AssertionError


@pytest.mark.api
class TestIndexCommand:
    """Test index command."""

    def test_index(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(index, [], obj=client_obj)
        if not (result.exit_code == 0):
            raise AssertionError
        if not (len(result.output) > 0):
            raise AssertionError

    def test_index_json(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(index, ["--json"], obj=client_obj)
        if not (result.exit_code == 0):
            raise AssertionError

        data = json.loads(result.output)
        if "total" not in data:
            raise AssertionError
        if "result" not in data:
            raise AssertionError

    def test_index_xml(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(index, ["--xml"], obj=client_obj)
        if not (result.exit_code == 0):
            raise AssertionError

        root = ET.fromstring(result.output)
        if not (root.tag == "response"):
            raise AssertionError
