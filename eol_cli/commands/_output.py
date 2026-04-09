"""Shared output formatting helpers for CLI commands."""

from collections.abc import Callable
from typing import Any

import click

from eol_cli.domain.errors import OutputSelectionError
from eol_cli.domain.output import (
    OutputFormatCommand,
    RenderOutputCommand,
    resolve_output_mode,
)
from eol_cli.formatters import format_json, format_sarif, format_xml


def _serialize_json(data: dict[str, object]) -> str:
    return format_json(data)


def _serialize_xml(data: dict[str, object]) -> str:
    return format_xml(data)


def _serialize_sarif(data: dict[str, object]) -> str:
    return format_sarif(data)


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
    try:
        resolve_output_mode(output_json, output_xml, output_sarif)
    except OutputSelectionError as exc:
        raise click.UsageError(str(exc)) from exc


def emit(
    data: dict[str, object],
    output_json: bool,
    output_xml: bool,
    rich_fn: Callable[..., None],
    output_sarif: bool = False,
    **rich_kwargs: Any,
) -> None:
    """Dispatch output to the appropriate formatter."""
    if not isinstance(data, dict):
        raise TypeError("emit expects a dictionary payload")

    command = RenderOutputCommand(
        output_format_command=OutputFormatCommand(
            to_json=_serialize_json,
            to_xml=_serialize_xml,
            to_sarif=_serialize_sarif,
        )
    )
    try:
        result = command.run(data, output_json, output_xml, output_sarif)
    except OutputSelectionError as exc:
        raise click.UsageError(str(exc)) from exc

    if result.is_rich:
        rich_fn(result.rich_payload, **rich_kwargs)
    else:
        click.echo(result.payload)
