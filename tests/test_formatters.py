"""Tests for formatters"""

import json
import xml.etree.ElementTree as ET
from contextlib import redirect_stdout
from io import StringIO

from eol_cli.api.client import EOLClient
from eol_cli.formatters import rich_formatter
from eol_cli.formatters.json_formatter import format_json
from eol_cli.formatters.xml_formatter import format_xml


class TestJSONFormatter:
    """Test JSON formatter."""

    def test_format_json_basic_dict(self):
        """Test JSON formatting with basic dictionary."""
        data = {"key": "value", "number": 42}
        result = format_json(data)

        # Should be valid JSON
        parsed = json.loads(result)
        assert parsed == data

        # Should be pretty-printed
        assert "\n" in result
        assert "  " in result

    def test_format_json_nested_structure(self):
        """Test JSON formatting with nested structure."""
        data = {"level1": {"level2": {"level3": "deep value"}}, "array": [1, 2, 3]}
        result = format_json(data)
        parsed = json.loads(result)
        assert parsed == data
        assert parsed["level1"]["level2"]["level3"] == "deep value"

    def test_format_json_with_unicode(self):
        """Test JSON formatting with Unicode characters."""
        data = {"name": "Python 🐍", "version": "3.14", "emoji": "✨"}
        result = format_json(data)

        parsed = json.loads(result)
        assert parsed["name"] == "Python 🐍"
        assert parsed["emoji"] == "✨"

        # Should preserve Unicode characters
        assert "🐍" in result
        assert "✨" in result

    def test_format_json_custom_indent(self):
        """Test JSON formatting with custom indentation."""
        data = {"key": "value"}
        result = format_json(data, indent=4)

        # Should use 4 spaces for indentation
        assert "    " in result

    def test_format_json_with_null_values(self):
        """Test JSON formatting with null values."""
        data = {"key": None, "value": "test"}
        result = format_json(data)
        parsed = json.loads(result)
        assert parsed["key"] is None
        assert "null" in result

    def test_format_json_with_real_api_data(self):
        """Test JSON formatting with real API data."""
        with EOLClient() as client:
            data = client.get_product_latest_release("python")
            result = format_json(data)

            # Should be valid JSON
            parsed = json.loads(result)
            assert "schema_version" in parsed
            assert "result" in parsed


class TestXMLFormatter:
    """Test XML formatter."""

    def test_format_xml_basic_dict(self):
        """Test XML formatting with basic dictionary."""
        data = {"key": "value", "number": 42}
        result = format_xml(data)

        # Should be valid XML
        root = ET.fromstring(result)
        assert root.tag == "response"

        # Check values
        key_elem = root.find("key")
        assert key_elem is not None
        assert key_elem.text == "value"

        number_elem = root.find("number")
        assert number_elem is not None
        assert number_elem.text == "42"

    def test_format_xml_nested_structure(self):
        """Test XML formatting with nested structure."""
        data = {"parent": {"child": "value"}}
        result = format_xml(data)
        root = ET.fromstring(result)

        parent = root.find("parent")
        assert parent is not None
        child = parent.find("child")
        assert child is not None
        assert child.text == "value"

    def test_format_xml_with_list(self):
        """Test XML formatting with lists."""
        data = {"items": ["item1", "item2", "item3"]}
        result = format_xml(data)
        root = ET.fromstring(result)

        items = root.find("items")
        assert items is not None
        item_elements = items.findall("item")
        assert len(item_elements) == 3
        assert item_elements[0].text == "item1"
        assert item_elements[1].text == "item2"

    def test_format_xml_with_null_values(self):
        """Test XML formatting with null values."""
        data = {"key": None, "value": "test"}
        result = format_xml(data)
        root = ET.fromstring(result)

        key_elem = root.find("key")
        assert key_elem is not None
        assert key_elem.get("nil") == "true"
        # Text can be None or empty string for nil elements
        assert key_elem.text in (None, "")

    def test_format_xml_pretty_print(self):
        """Test that XML is pretty printed."""
        data = {"key": "value"}
        result = format_xml(data, pretty=True)

        # Should have indentation
        assert "\n" in result
        assert "  " in result

    def test_format_xml_no_pretty_print(self):
        """Test XML without pretty printing."""
        data = {"key": "value"}
        result = format_xml(data, pretty=False)

        # Should be single line (mostly)
        lines = result.split("\n")
        assert len(lines) <= 2  # May have XML declaration

    def test_format_xml_with_real_api_data(self):
        """Test XML formatting with real API data."""
        with EOLClient() as client:
            data = client.get_product_latest_release("python")
            result = format_xml(data)

            # Should be valid XML
            root = ET.fromstring(result)
            assert root.tag == "response"

            # Check structure
            schema = root.find("schema_version")
            assert schema is not None

            result_elem = root.find("result")
            assert result_elem is not None


class TestRichFormatter:
    """Test Rich formatter functions."""

    def test_format_uri_list_with_real_data(self):
        """Test format_uri_list with real API data."""
        with EOLClient() as client:
            data = client.get_index()

            # Capture output
            output = StringIO()
            with redirect_stdout(output):
                rich_formatter.format_uri_list(data)

            result = output.getvalue()
            assert len(result) > 0

    def test_format_uri_list_empty_data(self):
        """Test format_uri_list with empty data."""
        data = {"result": [], "total": 0}

        output = StringIO()
        with redirect_stdout(output):
            rich_formatter.format_uri_list(data)

        result = output.getvalue()
        assert "No items found" in result or len(result) > 0

    def test_format_product_list_with_real_data(self):
        """Test format_product_list with real API data."""
        with EOLClient() as client:
            data = client.list_products()

            output = StringIO()
            with redirect_stdout(output):
                rich_formatter.format_product_list(data)

            result = output.getvalue()
            assert len(result) > 0

    def test_format_product_list_full_with_real_data(self):
        """Test format_product_list with full data."""
        with EOLClient() as client:
            data = client.list_products_full()

            output = StringIO()
            with redirect_stdout(output):
                rich_formatter.format_product_list(data, full=True)

            result = output.getvalue()
            assert len(result) > 0

    def test_format_product_details_with_real_data(self):
        """Test format_product_details with real API data."""
        with EOLClient() as client:
            data = client.get_product("python")

            output = StringIO()
            with redirect_stdout(output):
                rich_formatter.format_product_details(data, show_all=False)

            result = output.getvalue()
            assert len(result) > 0

    def test_format_product_details_show_all_with_real_data(self):
        """Test format_product_details with show_all=True."""
        with EOLClient() as client:
            data = client.get_product("python")

            output = StringIO()
            with redirect_stdout(output):
                rich_formatter.format_product_details(data, show_all=True)

            result = output.getvalue()
            assert len(result) > 0
            # When show_all is True, should have more content

    def test_format_release_details_with_real_data(self):
        """Test format_release_details with real API data."""
        with EOLClient() as client:
            data = client.get_product_release("python", "3.11")

            output = StringIO()
            with redirect_stdout(output):
                rich_formatter.format_release_details(data)

            result = output.getvalue()
            assert len(result) > 0

    def test_format_identifier_list_with_real_data(self):
        """Test format_identifier_list with real API data."""
        with EOLClient() as client:
            data = client.get_identifiers_by_type("purl")

            output = StringIO()
            with redirect_stdout(output):
                rich_formatter.format_identifier_list(data)

            result = output.getvalue()
            assert len(result) > 0

    def test_format_date_function(self):
        """Test _format_date helper function."""
        # Test with valid date
        result = rich_formatter._format_date("2024-01-01")
        assert "2024-01-01" in result

        # Test with None
        result = rich_formatter._format_date(None)
        assert "N/A" in result or result == ""

    def test_format_boolean_function(self):
        """Test _format_boolean helper function."""
        result_true = rich_formatter._format_boolean(True)
        assert len(result_true) > 0

        result_false = rich_formatter._format_boolean(False)
        assert len(result_false) > 0

    def test_format_eol_status_function(self):
        """Test _format_eol_status helper function."""
        result_eol = rich_formatter._format_eol_status(True, "2024-01-01")
        assert len(result_eol) > 0

        result_active = rich_formatter._format_eol_status(False, "2030-01-01")
        assert len(result_active) > 0


class TestFormattersIntegration:
    """Integration tests for all formatters."""

    def test_all_formatters_with_same_data(self):
        """Test that all formatters work with the same data."""
        with EOLClient() as client:
            data = client.get_product("python")

            # JSON formatting
            json_result = format_json(data)
            assert len(json_result) > 0
            json.loads(json_result)  # Validate JSON

            # XML formatting
            xml_result = format_xml(data)
            assert len(xml_result) > 0
            ET.fromstring(xml_result)  # Validate XML

            # Rich formatting
            output = StringIO()
            with redirect_stdout(output):
                rich_formatter.format_product_details(data)
            rich_result = output.getvalue()
            assert len(rich_result) > 0

    def test_formatters_with_multiple_products(self):
        """Test formatters with aggregated multiple product data."""
        with EOLClient() as client:
            data1 = client.get_product("python")
            data2 = client.get_product("nodejs")

            aggregated = {"schema_version": "1.2.0", "total": 2, "products": [data1, data2]}

            # JSON formatting
            json_result = format_json(aggregated)
            parsed = json.loads(json_result)
            assert parsed["total"] == 2
            assert len(parsed["products"]) == 2

            # XML formatting
            xml_result = format_xml(aggregated)
            root = ET.fromstring(xml_result)
            assert root.find("total").text == "2"
