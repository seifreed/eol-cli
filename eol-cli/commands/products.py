"""Products commands - Query for products."""

import click
import importlib

api_client = importlib.import_module("eol-cli.api.client")
formatters = importlib.import_module("eol-cli.formatters")

EOLClient = api_client.EOLClient
EOLAPIError = api_client.EOLAPIError
EOLNotFoundError = api_client.EOLNotFoundError
format_json = formatters.format_json
format_product_list = formatters.format_product_list
format_product_details = formatters.format_product_details
format_release_details = formatters.format_release_details


@click.group(name="products")
def products():
    """Query for products and their release cycles."""
    pass


@products.command(name="list")
@click.option(
    "--full",
    is_flag=True,
    help="Get full product details (includes all releases)"
)
@click.option(
    "--json",
    "output_json",
    is_flag=True,
    help="Output in JSON format"
)
def list_products(full: bool, output_json: bool):
    """List all products.
    
    By default, returns a summary of each product. Use --full to get
    complete product information including all release cycles.
    
    Examples:
        eol products list
        eol products list --full
        eol products list --json
    """
    client = EOLClient()
    
    try:
        if full:
            data = client.list_products_full()
        else:
            data = client.list_products()
        
        if output_json:
            click.echo(format_json(data))
        else:
            format_product_list(data, full=full)
    
    except EOLAPIError as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()
    finally:
        client.close()


@products.command(name="get")
@click.argument("product")
@click.option(
    "--json",
    "output_json",
    is_flag=True,
    help="Output in JSON format"
)
def get_product(product: str, output_json: bool):
    """Get detailed information about a specific product.
    
    PRODUCT: The product name (e.g., 'ubuntu', 'python', 'nodejs')
    
    Examples:
        eol products get ubuntu
        eol products get python
        eol products get nodejs --json
    """
    client = EOLClient()
    
    try:
        data = client.get_product(product)
        
        if output_json:
            click.echo(format_json(data))
        else:
            format_product_details(data)
    
    except EOLNotFoundError:
        click.echo(f"Error: Product '{product}' not found", err=True)
        click.echo("Tip: Use 'eol products list' to see available products", err=True)
        raise click.Abort()
    except EOLAPIError as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()
    finally:
        client.close()


@products.command(name="release")
@click.argument("product")
@click.argument("release")
@click.option(
    "--json",
    "output_json",
    is_flag=True,
    help="Output in JSON format"
)
def get_release(product: str, release: str, output_json: bool):
    """Get information about a specific product release cycle.
    
    PRODUCT: The product name (e.g., 'ubuntu', 'python')
    
    RELEASE: The release cycle name (e.g., '22.04', '3.11') or 'latest'
    
    Examples:
        eol products release ubuntu 22.04
        eol products release python 3.11
        eol products release ubuntu latest
        eol products release python latest --json
    """
    client = EOLClient()
    
    try:
        if release.lower() == "latest":
            data = client.get_product_latest_release(product)
        else:
            data = client.get_product_release(product, release)
        
        if output_json:
            click.echo(format_json(data))
        else:
            format_release_details(data)
    
    except EOLNotFoundError:
        if release.lower() == "latest":
            click.echo(f"Error: Product '{product}' not found", err=True)
        else:
            click.echo(
                f"Error: Release '{release}' not found for product '{product}'",
                err=True
            )
        click.echo("Tip: Use 'eol products get <product>' to see available releases", err=True)
        raise click.Abort()
    except EOLAPIError as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()
    finally:
        client.close()

