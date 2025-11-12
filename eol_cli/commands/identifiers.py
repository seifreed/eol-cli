"""Identifiers commands - Query for products by identifiers."""

import click

from eol_cli.api.client import EOLAPIError, EOLClient, EOLNotFoundError
from eol_cli.formatters import format_identifier_list, format_json, format_uri_list, format_xml


@click.group(name="identifiers")
def identifiers():
    """Query for products by identifiers (PURL, CPE, etc.)."""
    pass


@identifiers.command(name="list")
@click.option("--json", "output_json", is_flag=True, help="Output in JSON format")
@click.option("--xml", "output_xml", is_flag=True, help="Output in XML format")
def list_identifier_types(output_json: bool, output_xml: bool):
    """List all available identifier types.

    Common identifier types include: purl, cpe, repology

    Examples:
        eol-cli identifiers list
        eol-cli identifiers list --json
        eol-cli identifiers list --xml
    """
    if output_json and output_xml:
        click.echo("Error: --json and --xml are mutually exclusive", err=True)
        raise click.Abort() from None

    client = EOLClient()

    try:
        data = client.list_identifier_types()

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


@identifiers.command(name="get")
@click.argument("identifier_type")
@click.option("--json", "output_json", is_flag=True, help="Output in JSON format")
@click.option("--xml", "output_xml", is_flag=True, help="Output in XML format")
def get_identifiers(identifier_type: str, output_json: bool, output_xml: bool):
    """Get all identifiers for a specific type.

    IDENTIFIER_TYPE: The identifier type (e.g., 'purl', 'cpe', 'repology')

    Examples:
        eol-cli identifiers get purl
        eol-cli identifiers get cpe
        eol-cli identifiers get repology --json
        eol-cli identifiers get purl --xml
    """
    if output_json and output_xml:
        click.echo("Error: --json and --xml are mutually exclusive", err=True)
        raise click.Abort() from None

    client = EOLClient()

    try:
        data = client.get_identifiers_by_type(identifier_type)

        if output_json:
            click.echo(format_json(data))
        elif output_xml:
            click.echo(format_xml(data))
        else:
            format_identifier_list(data)

    except EOLNotFoundError:
        click.echo(f"Error: Identifier type '{identifier_type}' not found", err=True)
        click.echo("Tip: Use 'eol-cli identifiers list' to see available types", err=True)
        raise click.Abort() from None
    except EOLAPIError as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort() from None
    finally:
        client.close()
