"""Categories commands - Query for products by category."""

import click

from eol_cli.api.client import EOLAPIError, EOLNotFoundError
from eol_cli.commands._output import emit, format_options, validate_format_options
from eol_cli.formatters import format_product_list, format_uri_list


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
    validate_format_options(output_json, output_xml, output_sarif)
    client = ctx.obj["client"]
    try:
        data = client.list_categories()
        emit(data, output_json, output_xml, format_uri_list, output_sarif=output_sarif)
    except EOLAPIError as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort() from None


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
    validate_format_options(output_json, output_xml, output_sarif)
    client = ctx.obj["client"]
    try:
        data = client.get_category_products(category)
        emit(data, output_json, output_xml, format_product_list, output_sarif=output_sarif)
    except EOLNotFoundError:
        click.echo(f"Error: Category '{category}' not found", err=True)
        click.echo(
            "Tip: Use 'eol-cli categories list' to see available categories", err=True
        )
        raise click.Abort() from None
    except EOLAPIError as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort() from None
