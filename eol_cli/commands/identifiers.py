"""Identifiers commands - Query for products by identifiers."""

import click

from eol_cli.application import GetIdentifiersByTypeCommand, ListIdentifierTypesCommand
from eol_cli.commands._errors import handle_command_errors
from eol_cli.commands._output import emit, format_options
from eol_cli.formatters import format_identifier_list, format_uri_list
from eol_cli.infrastructure import EOLIdentifierGatewayAdapter
from eol_cli.presentation.responses import response_payload


@click.group(name="identifiers")
@click.pass_context
def identifiers(ctx: click.Context) -> None:
    """Query for products by identifiers (PURL, CPE, etc.)."""
    pass


@identifiers.command(name="list")
@format_options
@click.pass_context
def list_identifier_types(
    ctx: click.Context, output_json: bool, output_xml: bool, output_sarif: bool
) -> None:
    """List all available identifier types.

    Common identifier types include: purl, cpe, repology

    Examples:
        eol-cli identifiers list
        eol-cli identifiers list --json
        eol-cli identifiers list --sarif
    """
    client = ctx.obj["client"]
    with handle_command_errors():
        use_case = ListIdentifierTypesCommand(
            identifier_gateway=EOLIdentifierGatewayAdapter(client)
        )
        data = use_case.run()
        emit(
            response_payload(data),
            output_json,
            output_xml,
            format_uri_list,
            output_sarif=output_sarif,
        )


@identifiers.command(name="get")
@click.argument("identifier_type")
@format_options
@click.pass_context
def get_identifiers(
    ctx: click.Context,
    identifier_type: str,
    output_json: bool,
    output_xml: bool,
    output_sarif: bool,
) -> None:
    """Get all identifiers for a specific type.

    IDENTIFIER_TYPE: The identifier type (e.g., 'purl', 'cpe', 'repology')

    Examples:
        eol-cli identifiers get purl
        eol-cli identifiers get cpe
        eol-cli identifiers get repology --json
        eol-cli identifiers get purl --sarif
    """
    client = ctx.obj["client"]
    with handle_command_errors(on_not_found=lambda: _emit_identifier_not_found(identifier_type)):
        use_case = GetIdentifiersByTypeCommand(
            identifier_gateway=EOLIdentifierGatewayAdapter(client)
        )
        data = use_case.run(identifier_type)
        emit(
            response_payload(data),
            output_json,
            output_xml,
            format_identifier_list,
            output_sarif=output_sarif,
        )


def _emit_identifier_not_found(identifier_type: str) -> None:
    click.echo(f"Error: Identifier type '{identifier_type}' not found", err=True)
    click.echo("Tip: Use 'eol-cli identifiers list' to see available types", err=True)
