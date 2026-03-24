"""Identifiers commands - Query for products by identifiers."""

import click

from eol_cli.api.client import EOLAPIError, EOLNotFoundError
from eol_cli.commands._output import emit, format_options, validate_format_options
from eol_cli.formatters import format_identifier_list, format_uri_list


@click.group(name="identifiers")
@click.pass_context
def identifiers(ctx: click.Context) -> None:
    """Query for products by identifiers (PURL, CPE, etc.)."""
    pass


@identifiers.command(name="list")
@format_options
@click.pass_context
def list_identifier_types(ctx: click.Context, output_json: bool, output_xml: bool) -> None:
    """List all available identifier types.

    Common identifier types include: purl, cpe, repology

    Examples:
        eol-cli identifiers list
        eol-cli identifiers list --json
        eol-cli identifiers list --xml
    """
    validate_format_options(output_json, output_xml)
    client = ctx.obj["client"]
    try:
        data = client.list_identifier_types()
        emit(data, output_json, output_xml, format_uri_list)
    except EOLAPIError as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort() from None


@identifiers.command(name="get")
@click.argument("identifier_type")
@format_options
@click.pass_context
def get_identifiers(ctx: click.Context, identifier_type: str, output_json: bool, output_xml: bool) -> None:
    """Get all identifiers for a specific type.

    IDENTIFIER_TYPE: The identifier type (e.g., 'purl', 'cpe', 'repology')

    Examples:
        eol-cli identifiers get purl
        eol-cli identifiers get cpe
        eol-cli identifiers get repology --json
        eol-cli identifiers get purl --xml
    """
    validate_format_options(output_json, output_xml)
    client = ctx.obj["client"]
    try:
        data = client.get_identifiers_by_type(identifier_type)
        emit(data, output_json, output_xml, format_identifier_list)
    except EOLNotFoundError:
        click.echo(f"Error: Identifier type '{identifier_type}' not found", err=True)
        click.echo("Tip: Use 'eol-cli identifiers list' to see available types", err=True)
        raise click.Abort() from None
    except EOLAPIError as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort() from None
