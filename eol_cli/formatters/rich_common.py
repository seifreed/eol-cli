"""Shared helpers for Rich terminal output formatters."""

from datetime import datetime

from rich.console import Console

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
        return f"[yellow]{date_str}[/yellow] [dim](invalid date format)[/dim]"


def _format_boolean(value: bool, true_label: str = "Yes", false_label: str = "No") -> str:
    """Format a boolean value with colors."""
    if value:
        return f"[green]{true_label}[/green]"
    return f"[dim]{false_label}[/dim]"


def _format_eol_status(is_eol: bool, eol_from: str | None) -> str:
    """Format EOL status with color coding."""
    if is_eol:
        if eol_from:
            return f"[red]EOL[/red] ({_format_date(eol_from)})"
        return "[red]EOL[/red]"

    if not eol_from:
        return "[green]Active[/green] (no EOL date scheduled)"
    return f"[green]Active[/green] (EOL: {_format_date(eol_from)})"
