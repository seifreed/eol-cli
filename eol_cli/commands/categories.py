"""Categories commands - Query for products by category."""

import click

from eol_cli.application import GetCategoryProductsCommand, ListCategoriesCommand
from eol_cli.commands._errors import handle_command_errors
from eol_cli.commands._output import emit, format_options
from eol_cli.formatters import format_product_list, format_uri_list
from eol_cli.infrastructure import EOLCategoryGatewayAdapter
from eol_cli.presentation.responses import response_payload


@click.group(name="categories")
@click.pass_context
def categories(ctx: click.Context) -> None:
    """Query for products by category."""
    pass


@categories.command(name="list")
@format_options
@click.pass_context
def list_categories(
    ctx: click.Context, output_json: bool, output_xml: bool, output_sarif: bool
) -> None:
    """List all available categories.

    Examples:
        eol-cli categories list
        eol-cli categories list --json
        eol-cli categories list --xml
        eol-cli categories list --sarif
    """
    client = ctx.obj["client"]
    with handle_command_errors():
        use_case = ListCategoriesCommand(category_gateway=EOLCategoryGatewayAdapter(client))
        data = use_case.run()
        emit(
            response_payload(data),
            output_json,
            output_xml,
            format_uri_list,
            output_sarif=output_sarif,
        )


@categories.command(name="get")
@click.argument("category")
@format_options
@click.pass_context
def get_category(
    ctx: click.Context, category: str, output_json: bool, output_xml: bool, output_sarif: bool
) -> None:
    """Get all products in a specific category.

    CATEGORY: The category name (e.g., 'os', 'app', 'framework', 'server-app')

    Examples:
        eol-cli categories get os
        eol-cli categories get framework
        eol-cli categories get database --json
        eol-cli categories get os --sarif
    """
    client = ctx.obj["client"]
    with handle_command_errors(on_not_found=lambda: _emit_category_not_found(category)):
        use_case = GetCategoryProductsCommand(category_gateway=EOLCategoryGatewayAdapter(client))
        data = use_case.run(category)
        emit(
            response_payload(data),
            output_json,
            output_xml,
            format_product_list,
            output_sarif=output_sarif,
        )


def _emit_category_not_found(category: str) -> None:
    click.echo(f"Error: Category '{category}' not found", err=True)
    click.echo("Tip: Use 'eol-cli categories list' to see available categories", err=True)
