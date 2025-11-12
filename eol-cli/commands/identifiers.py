"""Identifiers commands - Query for products by identifiers."""

import click
import importlib

api_client = importlib.import_module("eol-cli.api.client")
formatters = importlib.import_module("eol-cli.formatters")

EOLClient = api_client.EOLClient
EOLAPIError = api_client.EOLAPIError
EOLNotFoundError = api_client.EOLNotFoundError
format_json = formatters.format_json
format_uri_list = formatters.format_uri_list
format_identifier_list = formatters.format_identifier_list


@click.group(name="identifiers")
def identifiers():
    """Query for products by identifiers (PURL, CPE, etc.)."""
    pass


@identifiers.command(name="list")
@click.option(
    "--json",
    "output_json",
    is_flag=True,
    help="Output in JSON format"
)
def list_identifier_types(output_json: bool):
    """List all available identifier types.
    
    Common identifier types include: purl, cpe, repology
    
    Examples:
        eol identifiers list
        eol identifiers list --json
    """
    client = EOLClient()
    
    try:
        data = client.list_identifier_types()
        
        if output_json:
            click.echo(format_json(data))
        else:
            format_uri_list(data)
    
    except EOLAPIError as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()
    finally:
        client.close()


@identifiers.command(name="get")
@click.argument("identifier_type")
@click.option(
    "--json",
    "output_json",
    is_flag=True,
    help="Output in JSON format"
)
def get_identifiers(identifier_type: str, output_json: bool):
    """Get all identifiers for a specific type.
    
    IDENTIFIER_TYPE: The identifier type (e.g., 'purl', 'cpe', 'repology')
    
    Examples:
        eol identifiers get purl
        eol identifiers get cpe
        eol identifiers get repology --json
    """
    client = EOLClient()
    
    try:
        data = client.get_identifiers_by_type(identifier_type)
        
        if output_json:
            click.echo(format_json(data))
        else:
            format_identifier_list(data)
    
    except EOLNotFoundError:
        click.echo(f"Error: Identifier type '{identifier_type}' not found", err=True)
        click.echo("Tip: Use 'eol identifiers list' to see available types", err=True)
        raise click.Abort()
    except EOLAPIError as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()
    finally:
        client.close()

