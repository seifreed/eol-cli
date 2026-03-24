"""Tags commands - Query for products by tags."""

import click

from eol_cli.api.client import EOLAPIError, EOLNotFoundError
from eol_cli.commands._output import emit, format_options, validate_format_options
from eol_cli.formatters import format_product_list, format_uri_list


@click.group(name="tags")
@click.pass_context
def tags(ctx: click.Context) -> None:
    """Query for products by tags."""
    pass


@tags.command(name="list")
@format_options
@click.pass_context
def list_tags(
    ctx: click.Context, output_json: bool, output_xml: bool, output_sarif: bool
) -> None:
    """List all available tags.

    Examples:
        eol-cli tags list
        eol-cli tags list --json
        eol-cli tags list --sarif
    """
    validate_format_options(output_json, output_xml, output_sarif)
    client = ctx.obj["client"]
    try:
        data = client.list_tags()
        emit(data, output_json, output_xml, format_uri_list, output_sarif=output_sarif)
    except EOLAPIError as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort() from None


@tags.command(name="get")
@click.argument("tag")
@format_options
@click.pass_context
def get_tag(
    ctx: click.Context, tag: str, output_json: bool, output_xml: bool, output_sarif: bool
) -> None:
    """Get all products with a specific tag.

    TAG: The tag name (e.g., 'linux', 'database', 'google')

    Examples:
        eol-cli tags get linux
        eol-cli tags get database
        eol-cli tags get microsoft --json
        eol-cli tags get linux-distribution --sarif
    """
    validate_format_options(output_json, output_xml, output_sarif)
    client = ctx.obj["client"]
    try:
        data = client.get_tag_products(tag)
        emit(data, output_json, output_xml, format_product_list, output_sarif=output_sarif)
    except EOLNotFoundError:
        click.echo(f"Error: Tag '{tag}' not found", err=True)
        click.echo("Tip: Use 'eol-cli tags list' to see available tags", err=True)
        raise click.Abort() from None
    except EOLAPIError as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort() from None
