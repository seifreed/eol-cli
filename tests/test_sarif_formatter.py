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
        assert output["version"] == "2.1.0"
        assert "$schema" in output
        assert "oasis-open.org" in output["$schema"]
        assert len(output["runs"]) == 1
        assert "tool" in output["runs"][0]
        assert "results" in output["runs"][0]

    def test_tool_descriptor(self):
        data = {"result": []}
        output = json.loads(format_sarif(data))
        driver = output["runs"][0]["tool"]["driver"]
        assert driver["name"] == "eol-cli"
        assert "version" in driver
        assert "informationUri" in driver
        assert len(driver["rules"]) == 2

    def test_rules_have_required_fields(self):
        data = {"result": []}
        output = json.loads(format_sarif(data))
        rules = output["runs"][0]["tool"]["driver"]["rules"]
        for rule in rules:
            assert "id" in rule
            assert "name" in rule
            assert "shortDescription" in rule
            assert "text" in rule["shortDescription"]


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
        assert len(results) == 1
        assert results[0]["level"] == "error"
        assert results[0]["ruleId"] == "EOL001"
        assert "End of Life" in results[0]["message"]["text"]
        assert "python 3.8" in results[0]["message"]["text"]

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
        assert len(results) == 1
        assert results[0]["level"] == "note"
        assert results[0]["ruleId"] == "EOL002"
        assert "Active" in results[0]["message"]["text"]

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
        assert len(results) == 2
        levels = {r["level"] for r in results}
        assert levels == {"error", "note"}

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
        assert props["product"] == "python"
        assert props["release"] == "3.12"
        assert props["releaseDate"] == "2023-10-02"
        assert props["isEol"] is False
        assert props["isLts"] is False


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
        assert len(results) == 2
        products_in_results = {r["properties"]["product"] for r in results}
        assert products_in_results == {"python", "nodejs"}


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
        assert len(results) == 1
        assert results[0]["level"] == "note"
        msg = results[0]["message"]["text"]
        assert "3.11: Active" in msg
        # Should NOT duplicate: "3.11 3.11: Active"
        assert "3.11 3.11" not in msg


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
        assert len(results) == 2
        assert all(r["level"] == "note" for r in results)

    def test_empty_result(self):
        data = {"result": []}
        output = json.loads(format_sarif(data))
        assert output["runs"][0]["results"] == []


class TestSARIFOutputValid:
    """Test SARIF output is always valid JSON."""

    def test_output_is_valid_json(self):
        data = {"result": {"name": "test", "releases": []}}
        output = format_sarif(data)
        parsed = json.loads(output)
        assert isinstance(parsed, dict)

    def test_unrecognized_data_produces_empty_results(self):
        """Data that doesn't match any known shape returns no results."""
        data = {"result": "just a string"}
        output = json.loads(format_sarif(data))
        assert output["runs"][0]["results"] == []


@pytest.mark.api
class TestSARIFCLIIntegration:
    """Test --sarif flag through CLI."""

    def test_products_get_sarif(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(products, ["get", "python", "--sarif"], obj=client_obj)
        assert result.exit_code == 0
        sarif = json.loads(result.output)
        assert sarif["version"] == "2.1.0"
        assert len(sarif["runs"][0]["results"]) > 0

    def test_products_release_sarif(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(
            products, ["release", "python", "3.11", "--sarif"], obj=client_obj
        )
        assert result.exit_code == 0
        sarif = json.loads(result.output)
        assert len(sarif["runs"][0]["results"]) == 1

    def test_sarif_json_mutually_exclusive(self, client_obj):
        runner = CliRunner()
        result = runner.invoke(
            products, ["get", "python", "--sarif", "--json"], obj=client_obj
        )
        assert result.exit_code == 2
        assert "mutually exclusive" in result.output.lower()
