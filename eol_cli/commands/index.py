"""Index command - Get API endpoints."""

import click

from eol_cli.application import GetIndexCommand
from eol_cli.commands._errors import handle_command_errors
from eol_cli.commands._output import emit, format_options
from eol_cli.formatters import format_uri_list
from eol_cli.infrastructure import EOLIndexGatewayAdapter
from eol_cli.presentation.responses import response_payload


@click.command(name="index")
@format_options
@click.pass_context
def index(ctx: click.Context, output_json: bool, output_xml: bool, output_sarif: bool) -> None:
    """Get the API index with main endpoints."""
    client = ctx.obj["client"]
    with handle_command_errors():
        use_case = GetIndexCommand(index_gateway=EOLIndexGatewayAdapter(client))
        data = use_case.run()
        emit(
            response_payload(data),
            output_json,
            output_xml,
            format_uri_list,
            output_sarif=output_sarif,
        )
