"""Output formatters for CLI."""

import importlib

json_formatter = importlib.import_module("eol-cli.formatters.json_formatter")
rich_formatter = importlib.import_module("eol-cli.formatters.rich_formatter")

format_json = json_formatter.format_json
format_uri_list = rich_formatter.format_uri_list
format_product_list = rich_formatter.format_product_list
format_product_details = rich_formatter.format_product_details
format_release_details = rich_formatter.format_release_details
format_identifier_list = rich_formatter.format_identifier_list

__all__ = [
    "format_json",
    "format_uri_list",
    "format_product_list",
    "format_product_details",
    "format_release_details",
    "format_identifier_list",
]

