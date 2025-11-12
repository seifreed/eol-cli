"""Categories commands - Query for products by category."""

import click

from eol_cli.api.client import EOLAPIError, EOLClient, EOLNotFoundError
from eol_cli.formatters import format_json, format_product_list, format_uri_list, format_xml


@click.group(name="categories")
def categories():
    """Query for products by category."""
    pass


@categories.command(name="list")
@click.option("--json", "output_json", is_flag=True, help="Output in JSON format")
@click.option("--xml", "output_xml", is_flag=True, help="Output in XML format")
def list_categories(output_json: bool, output_xml: bool):
    """List all available categories.

    Examples:
        eol-cli categories list
        eol-cli categories list --json
        eol-cli categories list --xml
    """
    if output_json and output_xml:
        click.echo("Error: --json and --xml are mutually exclusive", err=True)
        raise click.Abort() from None

    client = EOLClient()

    try:
        data = client.list_categories()

        if output_json:
            click.echo(format_json(data))
        elif output_xml:
            click.echo(format_xml(data))
        else:
            format_uri_list(data)

    except EOLAPIError as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort() from None
    finally:
        client.close()


@categories.command(name="get")
@click.argument("category")
@click.option("--json", "output_json", is_flag=True, help="Output in JSON format")
@click.option("--xml", "output_xml", is_flag=True, help="Output in XML format")
def get_category(category: str, output_json: bool, output_xml: bool):
    """Get all products in a specific category.

    CATEGORY: The category name (e.g., 'os', 'app', 'framework', 'server-app')

    Examples:
        eol-cli categories get os
        eol-cli categories get framework
        eol-cli categories get database --json
        eol-cli categories get os --xml
    """
    if output_json and output_xml:
        click.echo("Error: --json and --xml are mutually exclusive", err=True)
        raise click.Abort() from None

    client = EOLClient()

    try:
        data = client.get_category_products(category)

        if output_json:
            click.echo(format_json(data))
        elif output_xml:
            click.echo(format_xml(data))
        else:
            format_product_list(data)

    except EOLNotFoundError:
        click.echo(f"Error: Category '{category}' not found", err=True)
        click.echo("Tip: Use 'eol-cli categories list' to see available categories", err=True)
        raise click.Abort() from None
    except EOLAPIError as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort() from None
    finally:
        client.close()
