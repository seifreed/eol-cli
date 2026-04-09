"""Rich terminal output formatter facade."""

from eol_cli.formatters.rich_common import _format_boolean, _format_date, _format_eol_status
from eol_cli.formatters.rich_lists import (
    format_identifier_list,
    format_product_list,
    format_uri_list,
)
from eol_cli.formatters.rich_products import (
    format_product_details,
    format_product_suggestions,
)
from eol_cli.formatters.rich_releases import format_release_details

__all__ = [
    "_format_boolean",
    "_format_date",
    "_format_eol_status",
    "format_identifier_list",
    "format_product_details",
    "format_product_list",
    "format_product_suggestions",
    "format_release_details",
    "format_uri_list",
]
