"""Rich formatters for release detail outputs."""

from typing import Any

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from eol_cli.formatters.rich_common import _default_console, _format_boolean, _format_date


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

    if "isEoas" in result:
        info_table.add_row("Active Support Ended", _format_boolean(result.get("isEoas", False)))
        if result.get("eoasFrom"):
            info_table.add_row("EOAS Date", _format_date(result["eoasFrom"]))

    info_table.add_row(
        "End of Life", _format_boolean(result.get("isEol", False), "Yes (EOL)", "No (Active)")
    )
    info_table.add_row("EOL Date", _format_date(result.get("eolFrom")))

    if "isEoes" in result:
        is_eoes = result.get("isEoes")
        if is_eoes is not None:
            info_table.add_row("Extended Support Ended", _format_boolean(is_eoes))
        if result.get("eoesFrom"):
            info_table.add_row("EOES Date", _format_date(result["eoesFrom"]))

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

    header = Panel(
        f"[bold cyan]{result.get('label', result.get('name', 'Unknown'))}[/bold cyan]",
        box=box.DOUBLE,
        border_style="cyan",
    )
    c.print(header)

    info_table = _build_release_info_table(result)
    _add_support_status(info_table, result)

    c.print(Panel(info_table, title="[bold]Release Information[/bold]", border_style="blue"))

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

    custom = result.get("custom")
    if custom and isinstance(custom, dict):
        custom_table = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
        custom_table.add_column("Field", style="bold")
        custom_table.add_column("Value", style="cyan")

        for key, value in custom.items():
            custom_table.add_row(key, str(value) if value is not None else "N/A")

        c.print(Panel(custom_table, title="[bold]Custom Fields[/bold]", border_style="magenta"))
