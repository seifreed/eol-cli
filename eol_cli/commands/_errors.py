"""Shared CLI error handling helpers."""

from collections.abc import Callable, Iterator
from contextlib import contextmanager

import click

from eol_cli.domain import GatewayError, NotFoundError, ProductLookupError


@contextmanager
def handle_command_errors(on_not_found: Callable[[], None] | None = None) -> Iterator[None]:
    """Convert domain errors into Click-friendly command failures."""
    try:
        yield
    except click.Abort:
        raise
    except click.UsageError:
        raise
    except NotFoundError as exc:
        if on_not_found is not None:
            on_not_found()
        else:
            click.echo(f"Error: {exc}", err=True)
        raise click.Abort() from None
    except (GatewayError, ProductLookupError) as exc:
        click.echo(f"Error: {exc}", err=True)
        raise click.Abort() from None
    except Exception as exc:
        click.echo(f"Error: {exc}", err=True)
        raise click.Abort() from None
