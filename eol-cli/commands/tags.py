"""Tags commands - Query for products by tags."""

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


@click.group(name="tags")
def tags():
    """Query for products by tags."""
    pass


@tags.command(name="list")
@click.option(
    "--json",
    "output_json",
    is_flag=True,
    help="Output in JSON format"
)
def list_tags(output_json: bool):
    """List all available tags.
    
    Examples:
        eol tags list
        eol tags list --json
    """
    client = EOLClient()
    
    try:
        data = client.list_tags()
        
        if output_json:
            click.echo(format_json(data))
        else:
            format_uri_list(data)
    
    except EOLAPIError as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()
    finally:
        client.close()


@tags.command(name="get")
@click.argument("tag")
@click.option(
    "--json",
    "output_json",
    is_flag=True,
    help="Output in JSON format"
)
def get_tag(tag: str, output_json: bool):
    """Get all products with a specific tag.
    
    TAG: The tag name (e.g., 'linux', 'database', 'google')
    
    Examples:
        eol tags get linux
        eol tags get database
        eol tags get microsoft --json
    """
    client = EOLClient()
    
    try:
        data = client.get_tag_products(tag)
        
        if output_json:
            click.echo(format_json(data))
        else:
            format_product_list(data)
    
    except EOLNotFoundError:
        click.echo(f"Error: Tag '{tag}' not found", err=True)
        click.echo("Tip: Use 'eol tags list' to see available tags", err=True)
        raise click.Abort()
    except EOLAPIError as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()
    finally:
        client.close()

