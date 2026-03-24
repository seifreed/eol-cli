"""Shared output formatting helpers for CLI commands."""

from collections.abc import Callable
from typing import Any

import click

from eol_cli.formatters import format_json, format_sarif, format_xml


def format_options(fn: Callable[..., Any]) -> Callable[..., Any]:
    """Add --json, --xml, and --sarif output format options to a command."""
    fn = click.option("--json", "output_json", is_flag=True, help="Output in JSON format")(fn)
    fn = click.option("--xml", "output_xml", is_flag=True, help="Output in XML format")(fn)
    fn = click.option(
        "--sarif", "output_sarif", is_flag=True, help="Output in SARIF v2.1.0 format"
    )(fn)
    return fn


def validate_format_options(
    output_json: bool, output_xml: bool, output_sarif: bool = False
) -> None:
    """Validate that at most one structured output format is selected."""
    selected = sum([output_json, output_xml, output_sarif])
    if selected > 1:
        raise click.UsageError("--json, --xml, and --sarif are mutually exclusive")


def emit(
    data: Any,
    output_json: bool,
    output_xml: bool,
    rich_fn: Callable[..., None],
    output_sarif: bool = False,
    **rich_kwargs: Any,
) -> None:
    """Dispatch output to the appropriate formatter.

    Callers must call validate_format_options() before this function.

    Args:
        data: The data to format
        output_json: Whether to output as JSON
        output_xml: Whether to output as XML
        rich_fn: The Rich formatter function for terminal output
        output_sarif: Whether to output as SARIF v2.1.0
        **rich_kwargs: Additional keyword arguments for the Rich formatter
    """
    if output_json:
        click.echo(format_json(data))
    elif output_xml:
        click.echo(format_xml(data))
    elif output_sarif:
        click.echo(format_sarif(data))
    else:
        rich_fn(data, **rich_kwargs)
