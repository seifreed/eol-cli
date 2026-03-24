"""Shared output formatting helpers for CLI commands."""

from collections.abc import Callable
from typing import Any

import click

from eol_cli.formatters import format_json, format_xml


def format_options(fn: Callable[..., Any]) -> Callable[..., Any]:
    """Add --json and --xml output format options to a command."""
    fn = click.option("--json", "output_json", is_flag=True, help="Output in JSON format")(fn)
    fn = click.option("--xml", "output_xml", is_flag=True, help="Output in XML format")(fn)
    return fn


def validate_format_options(output_json: bool, output_xml: bool) -> None:
    """Validate that --json and --xml are not both set."""
    if output_json and output_xml:
        raise click.UsageError("--json and --xml are mutually exclusive")


def emit(
    data: Any,
    output_json: bool,
    output_xml: bool,
    rich_fn: Callable[..., None],
    **rich_kwargs: Any,
) -> None:
    """Dispatch output to the appropriate formatter.

    Callers must call validate_format_options() before this function.

    Args:
        data: The data to format
        output_json: Whether to output as JSON
        output_xml: Whether to output as XML
        rich_fn: The Rich formatter function for terminal output
        **rich_kwargs: Additional keyword arguments for the Rich formatter
    """
    if output_json:
        click.echo(format_json(data))
    elif output_xml:
        click.echo(format_xml(data))
    else:
        rich_fn(data, **rich_kwargs)
