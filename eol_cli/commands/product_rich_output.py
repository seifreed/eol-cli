"""Presentation helpers for Rich product output."""

import click

from eol_cli.formatters import format_product_details


def emit_product_rich_output(all_data: list[dict[str, object]], show_all: bool) -> None:
    """Render product lookup results in Rich format."""
    multi = len(all_data) > 1
    for index, data in enumerate(all_data):
        if index > 0:
            click.echo("\n" + "=" * 80 + "\n")
        format_product_details(data, show_all=show_all, show_header=multi)
