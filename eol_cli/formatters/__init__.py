"""Output formatters for CLI."""

from eol_cli.formatters.json_formatter import format_json
from eol_cli.formatters.rich_formatter import (
    format_identifier_list,
    format_product_details,
    format_product_list,
    format_product_suggestions,
    format_release_details,
    format_uri_list,
)
from eol_cli.formatters.sarif_formatter import format_sarif
from eol_cli.formatters.xml_formatter import format_xml

__all__ = [
    "format_json",
    "format_sarif",
    "format_xml",
    "format_uri_list",
    "format_product_list",
    "format_product_details",
    "format_product_suggestions",
    "format_release_details",
    "format_identifier_list",
]
