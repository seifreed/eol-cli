"""Tests for the SARIF v2.1.0 formatter."""

import json

import pytest
from click.testing import CliRunner

from eol_cli.commands.products import products
from eol_cli.formatters.sarif_formatter import format_sarif


class TestSARIFDocumentStructure:
    """Test SARIF document meets v2.1.0 spec."""

    def test_minimal_sarif_structure(self):
        data = {"result": []}
        output = json.loads(format_sarif(data))
        if not (output["version"] == "2.1.0"):
            raise AssertionError
        if "$schema" not in output:
            raise AssertionError
        if "oasis-open.org" not in output["$schema"]:
            raise AssertionError
        if not (len(output["runs"]) == 1):
            raise AssertionError
        if "tool" not in output["runs"][0]:
            raise AssertionError
        if "results" not in output["runs"][0]:
            raise AssertionError

    def test_tool_descriptor(self):
        data = {"result": []}
        output = json.loads(format_sarif(data))
        driver = output["runs"][0]["tool"]["driver"]
        if not (driver["name"] == "eol-cli"):
            raise AssertionError
        if "version" not in driver:
            raise AssertionError
        if "informationUri" not in driver:
            raise AssertionError
        if not (len(driver["rules"]) == 2):
            raise AssertionError

    def test_rules_have_required_fields(self):
        data = {"result": []}
        output = json.loads(format_sarif(data))
        rules = output["runs"][0]["tool"]["driver"]["rules"]
        for rule in rules:
            if "id" not in rule:
                raise AssertionError
            if "name" not in rule:
                raise AssertionError
            if "shortDescription" not in rule:
                raise AssertionError
            if "text" not in rule["shortDescription"]:
                raise AssertionError


class TestSARIFProductResults:
    """Test SARIF results for product data."""

    def test_eol_release_produces_error(self):
        data = {
            "result": {
                "name": "python",
                "label": "Python",
                "releases": [
                    {
                        "name": "3.8",
                        "label": "3.8",
                        "isEol": True,
                        "eolFrom": "2024-10-01",
                        "isLts": False,
                        "isMaintained": False,
                    }
                ],
            }
        }
        output = json.loads(format_sarif(data))
        results = output["runs"][0]["results"]
        if not (len(results) == 1):
            raise AssertionError
        if not (results[0]["level"] == "error"):
            raise AssertionError
        if not (results[0]["ruleId"] == "EOL001"):
            raise AssertionError
        if "End of Life" not in results[0]["message"]["text"]:
            raise AssertionError
        if "python 3.8" not in results[0]["message"]["text"]:
            raise AssertionError

    def test_active_release_produces_note(self):
        data = {
            "result": {
                "name": "python",
                "label": "Python",
                "releases": [
                    {
                        "name": "3.12",
                        "label": "3.12",
                        "isEol": False,
                        "eolFrom": "2028-10-01",
                        "isLts": False,
                        "isMaintained": True,
                    }
                ],
            }
        }
        output = json.loads(format_sarif(data))
        results = output["runs"][0]["results"]
        if not (len(results) == 1):
            raise AssertionError
        if not (results[0]["level"] == "note"):
            raise AssertionError
        if not (results[0]["ruleId"] == "EOL002"):
            raise AssertionError
        if "Active" not in results[0]["message"]["text"]:
            raise AssertionError

    def test_multiple_releases_produce_multiple_results(self):
        data = {
            "result": {
                "name": "python",
                "releases": [
                    {"name": "3.8", "isEol": True, "eolFrom": "2024-10-01"},
                    {"name": "3.12", "isEol": False, "eolFrom": "2028-10-01"},
                ],
            }
        }
        output = json.loads(format_sarif(data))
        results = output["runs"][0]["results"]
        if not (len(results) == 2):
            raise AssertionError
        levels = {r["level"] for r in results}
        if not (levels == {"error", "note"}):
            raise AssertionError

    def test_result_properties_contain_release_metadata(self):
        data = {
            "result": {
                "name": "python",
                "releases": [
                    {
                        "name": "3.12",
                        "releaseDate": "2023-10-02",
                        "isEol": False,
                        "eolFrom": "2028-10-01",
                        "isLts": False,
                        "isMaintained": True,
                    }
                ],
            }
        }
        output = json.loads(format_sarif(data))
        props = output["runs"][0]["results"][0]["properties"]
        if not (props["product"] == "python"):
            raise AssertionError
        if not (props["release"] == "3.12"):
            raise AssertionError
        if not (props["releaseDate"] == "2023-10-02"):
            raise AssertionError
        if props["isEol"] is not False:
            raise AssertionError
        if props["isLts"] is not False:
            raise AssertionError


class TestSARIFMultiProduct:
    """Test SARIF with multi-product aggregated responses."""

    def test_aggregated_products(self):
        data = {
            "total": 2,
            "products": [
                {
                    "result": {
                        "name": "python",
                        "releases": [{"name": "3.8", "isEol": True, "eolFrom": "2024-10-01"}],
                    }
                },
                {
                    "result": {
                        "name": "nodejs",
                        "releases": [{"name": "20", "isEol": False, "eolFrom": "2026-04-30"}],
                    }
                },
            ],
        }
        output = json.loads(format_sarif(data))
        results = output["runs"][0]["results"]
        if not (len(results) == 2):
            raise AssertionError
        products_in_results = {r["properties"]["product"] for r in results}
        if not (products_in_results == {"python", "nodejs"}):
            raise AssertionError


class TestSARIFSingleRelease:
    """Test SARIF with single release response (products release command)."""

    def test_single_release(self):
        data = {
            "result": {
                "name": "3.11",
                "label": "3.11",
                "isEol": False,
                "eolFrom": "2027-10-01",
                "isLts": False,
                "isMaintained": True,
                "releaseDate": "2022-10-24",
            }
        }
        output = json.loads(format_sarif(data))
        results = output["runs"][0]["results"]
        if not (len(results) == 1):
            raise AssertionError
        if not (results[0]["level"] == "note"):
            raise AssertionError
        msg = results[0]["message"]["text"]
        if "3.11: Active" not in msg:
            raise AssertionError
        # Should NOT duplicate: "3.11 3.11: Active"
        if not ("3.11 3.11" not in msg):
            raise AssertionError


class TestSARIFListResponses:
    """Test SARIF with list responses (categories, tags, index)."""

    def test_uri_list(self):
        data = {
            "result": [
                {"name": "products", "uri": "/api/v1/products"},
                {"name": "categories", "uri": "/api/v1/categories"},
            ]
        }
        output = json.loads(format_sarif(data))
        results = output["runs"][0]["results"]
        if not (len(results) == 2):
            raise AssertionError
        if not (all(r["level"] == "note" for r in results)):
            raise AssertionError

    def test_uri_list_with_non_dict_entries(self):
        data = {
            "result": [
                {"name": "products", "uri": "/api/v1/products"},
                "tag:legacy",
                42,
                None,
            ]
        }
        output = json.loads(format_sarif(data))
        results = output["runs"][0]["results"]
        if not (len(results) == 4):
            raise AssertionError
        if not (results[1]["message"]["text"].startswith("Item:")):
            raise AssertionError
        if not (results[2]["message"]["text"] == "Item: 42"):
            raise AssertionError
        if results[3]["properties"]["value"] is not None:
            raise AssertionError

    def test_empty_result(self):
        data = {"result": []}
        output = json.loads(format_sarif(data))
        if not (output["runs"][0]["results"] == []):
            raise AssertionError


class TestSARIFOutputValid:
    """Test SARIF output is always valid JSON."""

    def test_output_is_valid_json(self):
        data = {"result": {"name": "test", "releases": []}}
        output = format_sarif(data)
        parsed = json.loads(output)
        if not (isinstance(parsed, dict)):
            raise AssertionError

    def test_unrecognized_data_produces_empty_results(self):
        """Data that doesn't match any known shape returns no results."""
        data = {"result": "just a string"}
        output = json.loads(format_sarif(data))
        if not (output["runs"][0]["results"] == []):
            raise AssertionError


@pytest.mark.api
class TestSARIFCLIIntegration:
    """Test --sarif flag through CLI."""

    def test_products_get_sarif(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(products, ["get", "python", "--sarif"], obj=client_obj)
        if not (result.exit_code == 0):
            raise AssertionError
        sarif = json.loads(result.output)
        if not (sarif["version"] == "2.1.0"):
            raise AssertionError
        if not (len(sarif["runs"][0]["results"]) > 0):
            raise AssertionError

    def test_products_release_sarif(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(products, ["release", "python", "3.11", "--sarif"], obj=client_obj)
        if not (result.exit_code == 0):
            raise AssertionError
        sarif = json.loads(result.output)
        if not (len(sarif["runs"][0]["results"]) == 1):
            raise AssertionError

    def test_sarif_json_mutually_exclusive(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(products, ["get", "python", "--sarif", "--json"], obj=client_obj)
        if not (result.exit_code == 2):
            raise AssertionError
        if "mutually exclusive" not in result.output.lower():
            raise AssertionError
