"""Products commands - Query for products."""

from __future__ import annotations

from functools import partial

import click

from eol_cli.commands._output import format_options
from eol_cli.commands.product_rich_output import emit_product_rich_output
from eol_cli.commands.products_get import run_products_get
from eol_cli.commands.products_list import run_products_list
from eol_cli.commands.products_release import emit_release_not_found, run_products_release


@click.group(name="products")
@click.pass_context
def products(ctx: click.Context) -> None:
    """Query for products and their release cycles."""
    pass


@products.command(name="list")
@click.option("--full", is_flag=True, help="Get full product details (includes all releases)")
@format_options
@click.pass_context
def list_products(
    ctx: click.Context, full: bool, output_json: bool, output_xml: bool, output_sarif: bool
) -> None:
    """List all products.

    By default, returns a summary of each product. Use --full to get
    complete product information including all release cycles.

    Examples:
        eol products list
        eol products list --full
        eol products list --json
        eol products list --sarif
    """
    run_products_list(ctx.obj["client"], full, output_json, output_xml, output_sarif)


def _output_rich_format(all_data: list[dict[str, object]], show_all: bool) -> None:
    """Output products in Rich terminal format."""
    emit_product_rich_output(all_data, show_all)


@products.command(name="get")
@click.argument("product_names")
@click.option(
    "--all", "show_all", is_flag=True, help="Show all product details (info, links, identifiers)"
)
@format_options
@click.pass_context
def get_product(
    ctx: click.Context,
    product_names: str,
    output_json: bool,
    output_xml: bool,
    output_sarif: bool,
    show_all: bool,
) -> None:
    """Get detailed information about one or more products.

    By default, only shows the releases table. Use --all to see complete details.
    You can query multiple products by separating them with commas.

    PRODUCT_NAMES: One or more product names separated by commas (e.g., 'python', 'ubuntu,nodejs')

    Examples:
        eol-cli products get python
        eol-cli products get python --all
        eol-cli products get fortinet,apache
        eol-cli products get ubuntu,python,nodejs --json
        eol-cli products get apache,nginx --sarif
    """
    run_products_get(
        ctx.obj["client"],
        product_names,
        output_json,
        output_xml,
        output_sarif,
        show_all,
        rich_renderer=_output_rich_format,
    )


@products.command(name="release")
@click.argument("product")
@click.argument("release")
@format_options
@click.pass_context
def get_release(
    ctx: click.Context,
    product: str,
    release: str,
    output_json: bool,
    output_xml: bool,
    output_sarif: bool,
) -> None:
    """Get information about a specific product release cycle.

    PRODUCT: The product name (e.g., 'ubuntu', 'python')

    RELEASE: The release cycle name (e.g., '22.04', '3.11') or 'latest'

    Examples:
        eol-cli products release ubuntu 22.04
        eol-cli products release python 3.11
        eol-cli products release ubuntu latest
        eol-cli products release python latest --json
        eol-cli products release python latest --sarif
    """
    run_products_release(
        ctx.obj["client"],
        product,
        release,
        output_json,
        output_xml,
        output_sarif,
        on_not_found=partial(emit_release_not_found, product, release),
    )
