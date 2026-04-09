"""`products get` handler."""

from collections.abc import Callable

from eol_cli.api.client import EOLClient
from eol_cli.application import GetProductsCommand
from eol_cli.commands._errors import handle_command_errors
from eol_cli.commands.product_lookup_output import emit_product_lookup_result
from eol_cli.infrastructure import EOLProductGatewayAdapter


def run_products_get(
    client: EOLClient,
    product_names: str,
    output_json: bool,
    output_xml: bool,
    output_sarif: bool,
    show_all: bool,
    rich_renderer: Callable[[list[dict[str, object]], bool], None],
) -> None:
    """Execute the `products get` command."""
    with handle_command_errors():
        lookup_output = GetProductsCommand(product_gateway=EOLProductGatewayAdapter(client)).run(
            product_names
        )
        emit_product_lookup_result(
            lookup_output,
            output_json,
            output_xml,
            output_sarif,
            rich_renderer=rich_renderer,
            show_all=show_all,
        )
