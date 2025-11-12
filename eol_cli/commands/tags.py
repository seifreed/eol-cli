"""Tags commands - Query for products by tags."""

import click

from eol_cli.api.client import EOLAPIError, EOLClient, EOLNotFoundError
from eol_cli.formatters import format_json, format_product_list, format_uri_list, format_xml


@click.group(name="tags")
def tags():
    """Query for products by tags."""
    pass


@tags.command(name="list")
@click.option("--json", "output_json", is_flag=True, help="Output in JSON format")
@click.option("--xml", "output_xml", is_flag=True, help="Output in XML format")
def list_tags(output_json: bool, output_xml: bool):
    """List all available tags.

    Examples:
        eol-cli tags list
        eol-cli tags list --json
        eol-cli tags list --xml
    """
    if output_json and output_xml:
        click.echo("Error: --json and --xml are mutually exclusive", err=True)
        raise click.Abort() from None

    client = EOLClient()

    try:
        data = client.list_tags()

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


@tags.command(name="get")
@click.argument("tag")
@click.option("--json", "output_json", is_flag=True, help="Output in JSON format")
@click.option("--xml", "output_xml", is_flag=True, help="Output in XML format")
def get_tag(tag: str, output_json: bool, output_xml: bool):
    """Get all products with a specific tag.

    TAG: The tag name (e.g., 'linux', 'database', 'google')

    Examples:
        eol-cli tags get linux
        eol-cli tags get database
        eol-cli tags get microsoft --json
        eol-cli tags get linux-distribution --xml
    """
    if output_json and output_xml:
        click.echo("Error: --json and --xml are mutually exclusive", err=True)
        raise click.Abort() from None

    client = EOLClient()

    try:
        data = client.get_tag_products(tag)

        if output_json:
            click.echo(format_json(data))
        elif output_xml:
            click.echo(format_xml(data))
        else:
            format_product_list(data)

    except EOLNotFoundError:
        click.echo(f"Error: Tag '{tag}' not found", err=True)
        click.echo("Tip: Use 'eol-cli tags list' to see available tags", err=True)
        raise click.Abort() from None
    except EOLAPIError as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort() from None
    finally:
        client.close()
