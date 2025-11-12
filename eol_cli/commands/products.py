"""Products commands - Query for products."""

import click
from rich.console import Console
from rich.table import Table

from eol_cli.api.client import EOLAPIError, EOLClient, EOLNotFoundError
from eol_cli.formatters import (
    format_json,
    format_product_details,
    format_product_list,
    format_release_details,
    format_xml,
)
from eol_cli.utils import find_similar_products


@click.group(name="products")
def products():
    """Query for products and their release cycles."""
    pass


@products.command(name="list")
@click.option("--full", is_flag=True, help="Get full product details (includes all releases)")
@click.option("--json", "output_json", is_flag=True, help="Output in JSON format")
@click.option("--xml", "output_xml", is_flag=True, help="Output in XML format")
def list_products(full: bool, output_json: bool, output_xml: bool):
    """List all products.

    By default, returns a summary of each product. Use --full to get
    complete product information including all release cycles.

    Examples:
        eol products list
        eol products list --full
        eol products list --json
    """
    # Validate mutually exclusive format options
    if output_json and output_xml:
        click.echo("Error: --json and --xml are mutually exclusive", err=True)
        raise click.Abort() from None

    client = EOLClient()

    try:
        if full:
            data = client.list_products_full()
        else:
            data = client.list_products()

        if output_json:
            click.echo(format_json(data))
        elif output_xml:
            click.echo(format_xml(data))
        else:
            format_product_list(data, full=full)

    except EOLAPIError as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort() from None
    finally:
        client.close()


def _show_product_suggestions(product: str, all_products: list[str]):
    """Show suggestions for similar products using fuzzy matching.

    Args:
        product: The product name that was not found
        all_products: List of all available product names
    """
    suggestions = find_similar_products(product, all_products, threshold=0.3, max_results=5)

    if suggestions:
        console = Console(stderr=True)
        console.print("\n[yellow]Did you mean one of these?[/yellow]", highlight=False)

        table = Table(show_header=True, header_style="bold cyan", box=None, padding=(0, 2))
        table.add_column("Product", style="green", no_wrap=True)
        table.add_column("Similarity", justify="right", style="yellow")

        for suggested_product, score in suggestions:
            percentage = f"{score * 100:.1f}%"
            table.add_row(suggested_product, percentage)

        console.print(table)
        console.print(
            f"\n[dim]Try: eol-cli products get {suggestions[0][0]}[/dim]", highlight=False
        )


def _fetch_products(client: EOLClient, product_list: list[str]) -> tuple[list, list, dict]:
    """Fetch product data for multiple products.

    Returns:
        tuple: (all_data, errors, not_found) where all_data is list of successful fetches,
               errors is list of error messages, and not_found is dict of {product: error_msg}
    """
    all_data = []
    errors = []
    not_found = {}

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


def _create_aggregated_response(all_data: list) -> dict:
    """Create aggregated response for multiple products."""
    return {
        "schema_version": all_data[0].get("schema_version", "1.2.0"),
        "total": len(all_data),
        "products": all_data,
    }


def _output_json_format(all_data: list):
    """Output products in JSON format."""
    if len(all_data) == 1:
        click.echo(format_json(all_data[0]))
    else:
        click.echo(format_json(_create_aggregated_response(all_data)))


def _output_xml_format(all_data: list):
    """Output products in XML format."""
    if len(all_data) == 1:
        click.echo(format_xml(all_data[0]))
    else:
        click.echo(format_xml(_create_aggregated_response(all_data)))


def _output_rich_format(all_data: list, show_all: bool):
    """Output products in Rich terminal format."""
    for i, data in enumerate(all_data):
        if i > 0:
            click.echo("\n" + "=" * 80 + "\n")
        format_product_details(data, show_all=show_all)


def _handle_errors_and_suggestions(
    client: EOLClient, errors: list, not_found: dict, all_data: list
):
    """Handle errors and show suggestions for products not found.

    Args:
        client: EOL API client
        errors: List of error messages
        not_found: Dictionary of products not found
        all_data: List of successfully fetched data

    Raises:
        click.Abort: If no valid products were found
    """
    if not errors:
        return

    for error in errors:
        click.echo(f"Warning: {error}", err=True)

    # Show suggestions for products not found
    if not_found:
        try:
            products_data = client.list_products()
            all_products = [p["name"] for p in products_data.get("result", [])]
            for product in not_found.keys():
                _show_product_suggestions(product, all_products)
        except EOLAPIError:
            pass

    if not all_data:
        click.echo("\nNo valid products found", err=True)
        raise click.Abort() from None


@products.command(name="get")
@click.argument("products")
@click.option("--json", "output_json", is_flag=True, help="Output in JSON format")
@click.option("--xml", "output_xml", is_flag=True, help="Output in XML format")
@click.option(
    "--all", "show_all", is_flag=True, help="Show all product details (info, links, identifiers)"
)
def get_product(products: str, output_json: bool, output_xml: bool, show_all: bool):
    """Get detailed information about one or more products.

    By default, only shows the releases table. Use --all to see complete details.
    You can query multiple products by separating them with commas.

    PRODUCTS: One or more product names separated by commas (e.g., 'python', 'ubuntu,nodejs')

    Examples:
        eol-cli products get python
        eol-cli products get python --all
        eol-cli products get fortinet,apache
        eol-cli products get ubuntu,python,nodejs --json
        eol-cli products get apache,nginx --xml
    """
    if output_json and output_xml:
        click.echo("Error: --json and --xml are mutually exclusive", err=True)
        raise click.Abort() from None

    product_list = [p.strip() for p in products.split(",")]
    client = EOLClient()

    try:
        all_data, errors, not_found = _fetch_products(client, product_list)
        _handle_errors_and_suggestions(client, errors, not_found, all_data)

        if output_json:
            _output_json_format(all_data)
        elif output_xml:
            _output_xml_format(all_data)
        else:
            _output_rich_format(all_data, show_all)

    except click.Abort:
        raise
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort() from None
    finally:
        client.close()


@products.command(name="release")
@click.argument("product")
@click.argument("release")
@click.option("--json", "output_json", is_flag=True, help="Output in JSON format")
@click.option("--xml", "output_xml", is_flag=True, help="Output in XML format")
def get_release(product: str, release: str, output_json: bool, output_xml: bool):
    """Get information about a specific product release cycle.

    PRODUCT: The product name (e.g., 'ubuntu', 'python')

    RELEASE: The release cycle name (e.g., '22.04', '3.11') or 'latest'

    Examples:
        eol-cli products release ubuntu 22.04
        eol-cli products release python 3.11
        eol-cli products release ubuntu latest
        eol-cli products release python latest --json
        eol-cli products release python latest --xml
    """
    # Validate mutually exclusive format options
    if output_json and output_xml:
        click.echo("Error: --json and --xml are mutually exclusive", err=True)
        raise click.Abort() from None

    client = EOLClient()

    try:
        if release.lower() == "latest":
            data = client.get_product_latest_release(product)
        else:
            data = client.get_product_release(product, release)

        if output_json:
            click.echo(format_json(data))
        elif output_xml:
            click.echo(format_xml(data))
        else:
            format_release_details(data)

    except EOLNotFoundError:
        if release.lower() == "latest":
            click.echo(f"Error: Product '{product}' not found", err=True)
        else:
            click.echo(f"Error: Release '{release}' not found for product '{product}'", err=True)
        click.echo("Tip: Use 'eol-cli products get <product>' to see available releases", err=True)
        raise click.Abort() from None
    except EOLAPIError as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort() from None
    finally:
        client.close()
