"""Presentation helpers for product lookup output."""

from collections.abc import Callable

import click

from eol_cli.application import ProductGetOutput
from eol_cli.commands._output import emit
from eol_cli.formatters import format_product_details, format_product_suggestions
from eol_cli.presentation.responses import (
    create_aggregated_response,
    response_payload,
    response_payloads,
)


def _partial_summary_line(product_output: ProductGetOutput) -> str:
    """Build short partial result text for Rich output."""
    lookup_result = product_output.lookup_result
    summary = lookup_result.as_fetch_summary()
    return (
        f"Partial result: {summary['succeeded']}/{summary['requested']} "
        f"products found ({summary['failed']} failed)"
    )


def _fetch_summary_payload(product_output: ProductGetOutput) -> dict[str, object]:
    """Return the lookup summary payload for structured output metadata."""
    return product_output.lookup_result.as_fetch_summary()


def emit_product_lookup_feedback(product_output: ProductGetOutput) -> None:
    """Render lookup warnings and suggestions for product retrieval commands."""
    lookup_result = product_output.lookup_result
    if not lookup_result.summary.has_failures:
        return

    for warning in lookup_result.warnings:
        click.echo(warning, err=True)

    for error in lookup_result.summary.errors:
        click.echo(f"Warning: {error}", err=True)

    for product_name, suggestions in lookup_result.suggestions_by_product.items():
        format_product_suggestions(product_name, suggestions)


def emit_product_lookup_result(
    product_output: ProductGetOutput,
    output_json: bool,
    output_xml: bool,
    output_sarif: bool,
    rich_renderer: Callable[[list[dict[str, object]], bool], None],
    show_all: bool,
) -> None:
    """Render product lookup state in either structured or Rich format."""
    emit_product_lookup_feedback(product_output)

    lookup_result = product_output.lookup_result

    if lookup_result.summary.has_rejected:
        click.echo("\nNo valid products found", err=True)
        raise click.Abort() from None

    if output_json or output_xml or output_sarif:
        all_data = lookup_result.products
        data = all_data[0] if len(all_data) == 1 else create_aggregated_response(all_data)
        if lookup_result.summary.has_failures:
            data = data.with_meta(fetch_summary=_fetch_summary_payload(product_output))
        emit(
            response_payload(data),
            output_json,
            output_xml,
            format_product_details,
            output_sarif=output_sarif,
        )
        return

    payloads: list[dict[str, object]] = response_payloads(lookup_result.products)
    if lookup_result.summary.has_failures:
        click.echo(_partial_summary_line(product_output))
    rich_renderer(payloads, show_all)
