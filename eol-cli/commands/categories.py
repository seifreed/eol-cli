"""Categories commands - Query for products by category."""

import click
import importlib

api_client = importlib.import_module("eol-cli.api.client")
formatters = importlib.import_module("eol-cli.formatters")

EOLClient = api_client.EOLClient
EOLAPIError = api_client.EOLAPIError
EOLNotFoundError = api_client.EOLNotFoundError
format_json = formatters.format_json
format_uri_list = formatters.format_uri_list
format_product_list = formatters.format_product_list


@click.group(name="categories")
def categories():
    """Query for products by category."""
    pass


@categories.command(name="list")
@click.option(
    "--json",
    "output_json",
    is_flag=True,
    help="Output in JSON format"
)
def list_categories(output_json: bool):
    """List all available categories.
    
    Examples:
        eol categories list
        eol categories list --json
    """
    client = EOLClient()
    
    try:
        data = client.list_categories()
        
        if output_json:
            click.echo(format_json(data))
        else:
            format_uri_list(data)
    
    except EOLAPIError as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()
    finally:
        client.close()


@categories.command(name="get")
@click.argument("category")
@click.option(
    "--json",
    "output_json",
    is_flag=True,
    help="Output in JSON format"
)
def get_category(category: str, output_json: bool):
    """Get all products in a specific category.
    
    CATEGORY: The category name (e.g., 'os', 'app', 'framework', 'server-app')
    
    Examples:
        eol categories get os
        eol categories get framework
        eol categories get database --json
    """
    client = EOLClient()
    
    try:
        data = client.get_category_products(category)
        
        if output_json:
            click.echo(format_json(data))
        else:
            format_product_list(data)
    
    except EOLNotFoundError:
        click.echo(f"Error: Category '{category}' not found", err=True)
        click.echo("Tip: Use 'eol categories list' to see available categories", err=True)
        raise click.Abort()
    except EOLAPIError as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()
    finally:
        client.close()

