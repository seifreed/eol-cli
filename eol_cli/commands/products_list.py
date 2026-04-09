"""`products list` handler."""

from eol_cli.api.client import EOLClient
from eol_cli.application import ListProductsCommand
from eol_cli.commands._errors import handle_command_errors
from eol_cli.commands._output import emit
from eol_cli.formatters import format_product_list
from eol_cli.infrastructure import EOLProductGatewayAdapter
from eol_cli.presentation.responses import response_payload


def run_products_list(
    client: EOLClient,
    full: bool,
    output_json: bool,
    output_xml: bool,
    output_sarif: bool,
) -> None:
    """Execute the `products list` command."""
    with handle_command_errors():
        use_case = ListProductsCommand(product_catalog_gateway=EOLProductGatewayAdapter(client))
        data = use_case.run(full=full)
        emit(
            response_payload(data),
            output_json,
            output_xml,
            format_product_list,
            output_sarif=output_sarif,
            full=full,
        )
