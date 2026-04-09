"""`products release` handler."""

from collections.abc import Callable

import click

from eol_cli.api.client import EOLClient
from eol_cli.application import GetProductReleaseCommand
from eol_cli.commands._errors import handle_command_errors
from eol_cli.commands._output import emit
from eol_cli.formatters import format_release_details
from eol_cli.infrastructure import EOLProductGatewayAdapter
from eol_cli.presentation.responses import response_payload


def run_products_release(
    client: EOLClient,
    product: str,
    release: str,
    output_json: bool,
    output_xml: bool,
    output_sarif: bool,
    on_not_found: Callable[[], None],
) -> None:
    """Execute the `products release` command."""
    with handle_command_errors(on_not_found=on_not_found):
        use_case = GetProductReleaseCommand(
            product_release_gateway=EOLProductGatewayAdapter(client)
        )
        data = use_case.run(product, release)
        emit(
            response_payload(data),
            output_json,
            output_xml,
            format_release_details,
            output_sarif=output_sarif,
        )


def emit_release_not_found(product: str, release: str) -> None:
    """Render the not-found message for product release lookups."""
    if release.lower() == "latest":
        click.echo(f"Error: Product '{product}' not found", err=True)
    else:
        click.echo(f"Error: Release '{release}' not found for product '{product}'", err=True)
    click.echo("Tip: Use 'eol-cli products get <product>' to see available releases", err=True)
