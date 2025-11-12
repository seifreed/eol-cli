"""Index command - Get API endpoints."""

import click

from eol_cli.api.client import EOLAPIError, EOLClient
from eol_cli.formatters import format_json, format_uri_list, format_xml


@click.command(name="index")
@click.option("--json", "output_json", is_flag=True, help="Output in JSON format")
@click.option("--xml", "output_xml", is_flag=True, help="Output in XML format")
def index(output_json: bool, output_xml: bool):
    """Get the API index with main endpoints."""
    if output_json and output_xml:
        click.echo("Error: --json and --xml are mutually exclusive", err=True)
        raise click.Abort() from None

    client = EOLClient()

    try:
        data = client.get_index()

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
