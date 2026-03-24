"""Products commands - Query for products."""

from typing import Any

import click

from eol_cli.api.client import (
    API_SCHEMA_VERSION,
    EOLAPIError,
    EOLClient,
    EOLNotFoundError,
    EOLRateLimitError,
)
from eol_cli.commands._output import emit, format_options, validate_format_options
from eol_cli.formatters import (
    format_product_details,
    format_product_list,
    format_product_suggestions,
    format_release_details,
)
from eol_cli.utils import find_similar_products


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
    validate_format_options(output_json, output_xml, output_sarif)
    client = ctx.obj["client"]
    try:
        if full:
            data = client.list_products_full()
        else:
            data = client.list_products()

        emit(data, output_json, output_xml, format_product_list, output_sarif=output_sarif, full=full)

    except EOLAPIError as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort() from None


def _fetch_products(
    client: EOLClient, product_list: list[str]
) -> tuple[list[dict[str, Any]], list[str], dict[str, str]]:
    """Fetch product data for multiple products.

    Returns:
        tuple: (all_data, errors, not_found) where all_data is list of successful fetches,
               errors is list of error messages, and not_found is dict of {product: error_msg}
    """
    all_data: list[dict[str, Any]] = []
    errors: list[str] = []
    not_found: dict[str, str] = {}

    for product in product_list:
        try:
            data = client.get_product(product)
            all_data.append(data)
        except EOLNotFoundError:
            error_msg = f"Product '{product}' not found"
            errors.append(error_msg)
            not_found[product] = error_msg
        except EOLAPIError as e:
            errors.append(f"Error fetching '{product}': {e}")

    return all_data, errors, not_found


def _create_aggregated_response(all_data: list[dict[str, Any]]) -> dict[str, Any]:
    """Create aggregated response for multiple products."""
    return {
        "schema_version": all_data[0].get("schema_version", API_SCHEMA_VERSION),
        "total": len(all_data),
        "products": all_data,
    }


def _output_rich_format(all_data: list[dict[str, Any]], show_all: bool) -> None:
    """Output products in Rich terminal format."""
    multi = len(all_data) > 1
    for i, data in enumerate(all_data):
        if i > 0:
            click.echo("\n" + "=" * 80 + "\n")
        format_product_details(data, show_all=show_all, show_header=multi)


def _handle_errors_and_suggestions(
    client: EOLClient,
    errors: list[str],
    not_found: dict[str, str],
    all_data: list[dict[str, Any]],
) -> None:
    """Handle errors and show suggestions for products not found.

    Raises:
        click.Abort: If no valid products were found
    """
    if not errors:
        return

    for error in errors:
        click.echo(f"Warning: {error}", err=True)

    if not_found:
        try:
            products_data = client.list_products()
            all_products = [p.get("name", "") for p in products_data.get("result", [])]
            for product in not_found:
                suggestions = find_similar_products(product, all_products)
                format_product_suggestions(product, suggestions)
        except EOLRateLimitError as e:
            click.echo(f"(Rate limited, cannot fetch suggestions: {e})", err=True)
        except EOLAPIError as e:
            click.echo(f"(Could not fetch suggestions: {e})", err=True)

    if not all_data:
        click.echo("\nNo valid products found", err=True)
        raise click.Abort() from None


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
    validate_format_options(output_json, output_xml, output_sarif)

    product_list = [p.strip() for p in product_names.split(",") if p.strip()]

    if not product_list:
        click.echo("Error: No valid product names provided", err=True)
        raise click.Abort() from None

    client = ctx.obj["client"]
    try:
        all_data, errors, not_found = _fetch_products(client, product_list)
        _handle_errors_and_suggestions(client, errors, not_found, all_data)

        # For structured formats: aggregate multi-product results and use emit().
        # For Rich: iterate with separators (cannot be expressed as a single emit call).
        if output_json or output_xml or output_sarif:
            data = all_data[0] if len(all_data) == 1 else _create_aggregated_response(all_data)
            emit(data, output_json, output_xml, format_product_details, output_sarif=output_sarif)
        else:
            _output_rich_format(all_data, show_all)

    except click.Abort:
        raise
    except EOLAPIError as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort() from None


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
    validate_format_options(output_json, output_xml, output_sarif)
    client = ctx.obj["client"]
    try:
        if release.lower() == "latest":
            data = client.get_product_latest_release(product)
        else:
            data = client.get_product_release(product, release)

        emit(data, output_json, output_xml, format_release_details, output_sarif=output_sarif)

    except EOLNotFoundError:
        if release.lower() == "latest":
            click.echo(f"Error: Product '{product}' not found", err=True)
        else:
            click.echo(
                f"Error: Release '{release}' not found for product '{product}'", err=True
            )
        click.echo(
            "Tip: Use 'eol-cli products get <product>' to see available releases", err=True
        )
        raise click.Abort() from None
    except EOLAPIError as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort() from None
