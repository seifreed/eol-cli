"""Rich formatters for list-style outputs."""

from typing import Any

from rich import box
from rich.console import Console
from rich.table import Table

from eol_cli.formatters.rich_common import (
    _MAX_TAGS_DISPLAYED,
    _default_console,
)


def format_uri_list(data: dict[str, Any], *, console: Console | None = None) -> None:
    """Format and print a list of URIs."""
    c = console or _default_console
    result = data.get("result", [])
    total = data.get("total", len(result))

    if not result:
        c.print("[yellow]No items found[/yellow]")
        return

    table = Table(
        title=f"[bold]Results[/bold] ({total} items)",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold cyan",
    )

    table.add_column("Name", style="green")
    table.add_column("URI", style="blue")

    for item in result:
        table.add_row(item.get("name", ""), item.get("uri", ""))

    c.print(table)


def format_product_list(
    data: dict[str, Any], full: bool = False, *, console: Console | None = None
) -> None:
    """Format and print a list of products."""
    c = console or _default_console
    result = data.get("result", [])
    total = data.get("total", len(result))

    if not result:
        c.print("[yellow]No products found[/yellow]")
        return

    table = Table(
        title=f"[bold]Products[/bold] ({total} items)",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold cyan",
    )

    table.add_column("Name", style="green", no_wrap=True)
    table.add_column("Label", style="bold")
    table.add_column("Category", style="yellow")
    table.add_column("Tags", style="blue")

    if full:
        table.add_column("Releases", justify="right", style="magenta")

    for product in result:
        tags = product.get("tags") or []
        valid_tags = [t for t in tags if t is not None]
        tag_names = ", ".join(valid_tags[:_MAX_TAGS_DISPLAYED])
        if len(valid_tags) > _MAX_TAGS_DISPLAYED:
            tag_names += "..."

        name = product.get("name", "")
        label = product.get("label", "")
        category = product.get("category", "")

        if full:
            releases = product.get("releases", [])
            table.add_row(name, label, category, tag_names, str(len(releases)))
        else:
            table.add_row(name, label, category, tag_names)

    c.print(table)


def format_identifier_list(data: dict[str, Any], *, console: Console | None = None) -> None:
    """Format and print a list of identifiers."""
    c = console or _default_console
    result = data.get("result", [])
    total = data.get("total", len(result))

    if not result:
        c.print("[yellow]No identifiers found[/yellow]")
        return

    table = Table(
        title=f"[bold]Identifiers[/bold] ({total} items)",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold cyan",
    )

    table.add_column("Identifier", style="green")
    table.add_column("Product", style="blue")
    table.add_column("Product URI", style="dim")

    for item in result:
        product_data = item.get("product")
        product = product_data if isinstance(product_data, dict) else {}
        table.add_row(
            item.get("identifier", ""), product.get("name") or "N/A", product.get("uri") or ""
        )

    c.print(table)
