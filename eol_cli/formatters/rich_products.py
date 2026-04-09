"""Rich formatters for product-specific outputs."""

from typing import Any

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from eol_cli.formatters.rich_common import (
    _default_console,
    _default_stderr_console,
    _format_boolean,
    _format_date,
    _format_eol_status,
)


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
    tag_names = ", ".join(t for t in (result.get("tags") or []) if t is not None)
    info_table.add_row("Tags", tag_names or "N/A")
    aliases = ", ".join(a for a in (result.get("aliases") or []) if a is not None)
    info_table.add_row("Aliases", aliases or "N/A")

    version_cmd = result.get("versionCommand")
    if version_cmd:
        info_table.add_row("Version Command", f"[cyan]{version_cmd}[/cyan]")

    c.print(Panel(info_table, title="[bold]Product Information[/bold]", border_style="blue"))


def _print_product_links(links: dict[str, Any], c: Console) -> None:
    """Print product links."""
    if not isinstance(links, dict) or not links:
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
        if isinstance(identifier, dict):
            id_table.add_row(identifier.get("type", ""), identifier.get("id", ""))

    c.print(Panel(id_table, title="[bold]Identifiers[/bold]", border_style="blue"))


def _normalize_releases(data: dict[str, Any]) -> list[dict[str, Any]]:
    """Normalize release cycles payload to a list."""
    releases = data.get("releases", [])
    if not isinstance(releases, list):
        return []

    return releases


def _emit_full_product_sections(result: dict[str, Any], c: Console) -> None:
    """Emit detailed product sections for full output."""
    _print_product_header(result, c)
    _print_product_info(result, c)
    _print_product_links(result.get("links", {}), c)
    _print_product_identifiers(result.get("identifiers", []), c)
    c.print()  # Add spacing before releases


def _emit_release_cycles_heading(
    releases: list[dict[str, Any]], c: Console, show_all: bool
) -> None:
    """Emit heading for the release cycles table."""
    if show_all:
        c.print(f"[bold]Release Cycles[/bold] ({len(releases)} total)\n")


def _build_releases_table(releases: list[dict[str, Any]]) -> Table:
    """Build a table with release cycle details."""
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

    return releases_table


def _emit_releases_section(
    data: dict[str, Any], show_all: bool, show_header: bool, c: Console
) -> None:
    """Emit release cycles output for product details."""
    releases = _normalize_releases(data)
    if releases:
        _emit_release_cycles_heading(releases, c, show_all)
        c.print(_build_releases_table(releases))
        return

    _emit_missing_releases_header(show_all, show_header, data, c)
    c.print("[yellow]No release cycles found[/yellow]")


def _emit_missing_releases_header(
    show_all: bool, show_header: bool, data: dict[str, Any], c: Console
) -> None:
    """Emit a default header when showing only release output."""
    if not show_all and not show_header:
        _print_product_header(data, c)


def format_product_details(
    data: dict[str, Any],
    show_all: bool = False,
    show_header: bool = False,
    *,
    console: Console | None = None,
) -> None:
    """Format and print detailed product information."""
    c = console or _default_console
    result = data.get("result")

    if not isinstance(result, dict) or not result:
        c.print("[yellow]No data found[/yellow]")
        return

    if show_all:
        _emit_full_product_sections(result, c)
    elif show_header:
        _print_product_header(result, c)

    _emit_releases_section(result, show_all, show_header, c)


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
