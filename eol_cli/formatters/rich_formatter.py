"""Rich terminal output formatter."""

from datetime import datetime
from typing import Any

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

_default_console = Console()
_default_stderr_console = Console(stderr=True)

_MAX_TAGS_DISPLAYED = 3


def _format_date(date_str: str | None) -> str:
    """Format a date string for display."""
    if not date_str:
        return "[dim]N/A[/dim]"

    try:
        date_obj = datetime.fromisoformat(date_str)
        return date_obj.strftime("%Y-%m-%d")
    except (ValueError, TypeError):
        return date_str


def _format_boolean(value: bool, true_label: str = "Yes", false_label: str = "No") -> str:
    """Format a boolean value with colors."""
    if value:
        return f"[green]{true_label}[/green]"
    return f"[dim]{false_label}[/dim]"


def _format_eol_status(is_eol: bool, eol_from: str | None) -> str:
    """Format EOL status with color coding."""
    if is_eol:
        return f"[red]EOL[/red] ({_format_date(eol_from)})"
    return f"[green]Active[/green] (EOL: {_format_date(eol_from)})"


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
        tag_names = ", ".join(tags[:_MAX_TAGS_DISPLAYED])
        if len(tags) > _MAX_TAGS_DISPLAYED:
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


def _print_product_header(result: dict[str, Any], c: Console) -> None:
    """Print product header panel."""
    header = Panel(
        f"[bold cyan]{result.get('label', result.get('name', 'Unknown'))}[/bold cyan]\n"
        f"[dim]Product: {result.get('name', 'N/A')}[/dim]",
        box=box.DOUBLE,
        border_style="cyan",
    )
    c.print(header)


def _print_product_info(result: dict[str, Any], c: Console) -> None:
    """Print product basic information."""
    info_table = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
    info_table.add_column("Field", style="bold")
    info_table.add_column("Value")

    info_table.add_row("Category", result.get("category", "N/A"))
    tag_names = ", ".join(result.get("tags") or [])
    info_table.add_row("Tags", tag_names or "N/A")
    aliases = ", ".join(result.get("aliases") or [])
    info_table.add_row("Aliases", aliases or "None")

    version_cmd = result.get("versionCommand")
    if version_cmd:
        info_table.add_row("Version Command", f"[cyan]{version_cmd}[/cyan]")

    c.print(Panel(info_table, title="[bold]Product Information[/bold]", border_style="blue"))


def _print_product_links(links: dict[str, Any], c: Console) -> None:
    """Print product links."""
    if not links:
        return

    links_table = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
    links_table.add_column("Type", style="bold")
    links_table.add_column("URL", style="blue")

    if links.get("html"):
        links_table.add_row("Website", links["html"])
    if links.get("releasePolicy"):
        links_table.add_row("Release Policy", links["releasePolicy"])
    if links.get("icon"):
        links_table.add_row("Icon", links["icon"])

    c.print(Panel(links_table, title="[bold]Links[/bold]", border_style="blue"))


def _print_product_identifiers(identifiers: list[dict[str, Any]], c: Console) -> None:
    """Print product identifiers."""
    if not isinstance(identifiers, list) or not identifiers:
        return

    id_table = Table(box=box.SIMPLE, show_header=True, header_style="bold")
    id_table.add_column("Type", style="yellow")
    id_table.add_column("Identifier", style="green")

    for identifier in identifiers:
        id_table.add_row(identifier.get("type", ""), identifier.get("id", ""))

    c.print(Panel(id_table, title="[bold]Identifiers[/bold]", border_style="blue"))


def format_product_details(
    data: dict[str, Any],
    show_all: bool = False,
    show_header: bool = False,
    *,
    console: Console | None = None,
) -> None:
    """Format and print detailed product information."""
    c = console or _default_console
    result = data.get("result", {})

    if not result:
        c.print("[yellow]No data found[/yellow]")
        return

    if show_all:
        _print_product_header(result, c)
        _print_product_info(result, c)
        _print_product_links(result.get("links", {}), c)
        _print_product_identifiers(result.get("identifiers", []), c)
        c.print()  # Add spacing before releases
    elif show_header:
        _print_product_header(result, c)

    # Always show releases
    releases = result.get("releases", [])
    if releases:
        if show_all:
            c.print(f"[bold]Release Cycles[/bold] ({len(releases)} total)\n")

        releases_table = Table(box=box.ROUNDED, show_header=True, header_style="bold cyan")

        releases_table.add_column("Name", style="green")
        releases_table.add_column("Label", style="bold")
        releases_table.add_column("Released", style="blue")
        releases_table.add_column("LTS", justify="center")
        releases_table.add_column("Status", justify="center")
        releases_table.add_column("Latest", style="magenta")

        for release in releases:
            latest_info = release.get("latest")
            latest_version = "N/A"
            if latest_info:
                if isinstance(latest_info, dict):
                    latest_version = latest_info.get("name", "N/A")
                else:
                    latest_version = str(latest_info)

            releases_table.add_row(
                release.get("name", ""),
                release.get("label", ""),
                _format_date(release.get("releaseDate")),
                _format_boolean(release.get("isLts", False)),
                _format_eol_status(release.get("isEol", False), release.get("eolFrom")),
                latest_version,
            )

        c.print(releases_table)


def _build_release_info_table(result: dict[str, Any]) -> Table:
    """Build the main release information table."""
    info_table = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
    info_table.add_column("Field", style="bold", width=20)
    info_table.add_column("Value")

    info_table.add_row("Release Cycle", result.get("name", "N/A"))

    codename = result.get("codename")
    if codename:
        info_table.add_row("Codename", codename)

    info_table.add_row("Release Date", _format_date(result.get("releaseDate")))
    info_table.add_row("LTS", _format_boolean(result.get("isLts", False)))

    lts_from = result.get("ltsFrom")
    if lts_from:
        info_table.add_row("LTS From", _format_date(lts_from))

    return info_table


def _add_support_status(info_table: Table, result: dict[str, Any]) -> None:
    """Add support status information to the table."""
    info_table.add_row("", "")  # Separator
    info_table.add_row("[bold]Support Status[/bold]", "")

    info_table.add_row(
        "Maintained", _format_boolean(result.get("isMaintained", False), "Yes", "No")
    )

    # EOAS (End of Active Support)
    if "isEoas" in result:
        info_table.add_row("Active Support Ended", _format_boolean(result.get("isEoas", False)))
        if result.get("eoasFrom"):
            info_table.add_row("EOAS Date", _format_date(result["eoasFrom"]))

    # EOL
    info_table.add_row(
        "End of Life", _format_boolean(result.get("isEol", False), "Yes (EOL)", "No (Active)")
    )
    info_table.add_row("EOL Date", _format_date(result.get("eolFrom")))

    # EOES (End of Extended Support)
    if "isEoes" in result:
        is_eoes = result.get("isEoes")
        if is_eoes is not None:
            info_table.add_row("Extended Support Ended", _format_boolean(is_eoes))
        if result.get("eoesFrom"):
            info_table.add_row("EOES Date", _format_date(result["eoesFrom"]))

    # Discontinued (mainly for hardware)
    if "isDiscontinued" in result:
        info_table.add_row("Discontinued", _format_boolean(result.get("isDiscontinued", False)))
        if result.get("discontinuedFrom"):
            info_table.add_row("Discontinued Date", _format_date(result["discontinuedFrom"]))


def format_release_details(data: dict[str, Any], *, console: Console | None = None) -> None:
    """Format and print release cycle details."""
    c = console or _default_console
    result = data.get("result", {})

    if not result:
        c.print("[yellow]No data found[/yellow]")
        return

    # Header
    header = Panel(
        f"[bold cyan]{result.get('label', result.get('name', 'Unknown'))}[/bold cyan]",
        box=box.DOUBLE,
        border_style="cyan",
    )
    c.print(header)

    # Build and populate info table
    info_table = _build_release_info_table(result)
    _add_support_status(info_table, result)

    c.print(Panel(info_table, title="[bold]Release Information[/bold]", border_style="blue"))

    # Latest version
    latest = result.get("latest")
    if latest and isinstance(latest, dict):
        latest_table = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
        latest_table.add_column("Field", style="bold")
        latest_table.add_column("Value")

        latest_table.add_row("Version", latest.get("name", "N/A"))
        latest_table.add_row("Release Date", _format_date(latest.get("date")))

        if latest.get("link"):
            latest_table.add_row("Release Notes", f"[blue]{latest['link']}[/blue]")

        c.print(Panel(latest_table, title="[bold]Latest Version[/bold]", border_style="green"))

    # Custom fields
    custom = result.get("custom")
    if custom and isinstance(custom, dict):
        custom_table = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
        custom_table.add_column("Field", style="bold")
        custom_table.add_column("Value", style="cyan")

        for key, value in custom.items():
            custom_table.add_row(key, str(value) if value is not None else "N/A")

        c.print(Panel(custom_table, title="[bold]Custom Fields[/bold]", border_style="magenta"))


def format_product_suggestions(
    product: str,
    suggestions: list[tuple[str, float]],
    *,
    console: Console | None = None,
) -> None:
    """Display pre-computed product suggestions."""
    if not suggestions:
        return

    c = console or _default_stderr_console

    c.print("\n[yellow]Did you mean one of these?[/yellow]", highlight=False)

    table = Table(show_header=True, header_style="bold cyan", box=None, padding=(0, 2))
    table.add_column("Product", style="green", no_wrap=True)
    table.add_column("Similarity", justify="right", style="yellow")

    for suggested_product, score in suggestions:
        percentage = f"{score * 100:.1f}%"
        table.add_row(suggested_product, percentage)

    c.print(table)
    c.print(f"\n[dim]Try: eol-cli products get {suggestions[0][0]}[/dim]", highlight=False)


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
        product = item.get("product") or {}
        table.add_row(
            item.get("identifier", ""), product.get("name") or "N/A", product.get("uri") or ""
        )

    c.print(table)
