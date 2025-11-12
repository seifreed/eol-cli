"""Index command - Get API endpoints."""

import click
import importlib

api_client = importlib.import_module("eol-cli.api.client")
formatters = importlib.import_module("eol-cli.formatters")

EOLClient = api_client.EOLClient
EOLAPIError = api_client.EOLAPIError
format_json = formatters.format_json
format_uri_list = formatters.format_uri_list


@click.command(name="index")
@click.option(
    "--json",
    "output_json",
    is_flag=True,
    help="Output in JSON format"
)
def index(output_json: bool):
    """Get the API index with main endpoints."""
    client = EOLClient()
    
    try:
        data = client.get_index()
        
        if output_json:
            click.echo(format_json(data))
        else:
            format_uri_list(data)
    
    except EOLAPIError as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()
    finally:
        client.close()

