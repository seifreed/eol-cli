"""Index command - Get API endpoints."""

import click

from eol_cli.api.client import EOLAPIError
from eol_cli.commands._output import emit, format_options, validate_format_options
from eol_cli.formatters import format_uri_list


@click.command(name="index")
@format_options
@click.pass_context
def index(ctx: click.Context, output_json: bool, output_xml: bool) -> None:
    """Get the API index with main endpoints."""
    validate_format_options(output_json, output_xml)
    client = ctx.obj["client"]
    try:
        data = client.get_index()
        emit(data, output_json, output_xml, format_uri_list)
    except EOLAPIError as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort() from None
