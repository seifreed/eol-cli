"""Shared fixtures for eol-cli tests."""

from collections.abc import Callable, Generator
from io import StringIO

import pytest
from rich.console import Console

from eol_cli.api.client import EOLClient


@pytest.fixture
def client_obj(request: pytest.FixtureRequest) -> Generator[dict[str, EOLClient], None, None]:
    """Provide a shared EOLClient via Click's obj dict.

    Requires network access. Skips if the requesting test is not marked @pytest.mark.api.
    """
    marker = request.node.get_closest_marker("api")
    if marker is None:
        pytest.skip("Skipping: test requires @pytest.mark.api for network access")
    client = EOLClient()
    yield {"client": client}
    client.close()


@pytest.fixture
def make_console() -> Callable[[], tuple[StringIO, Console]]:
    """Factory fixture: returns a (StringIO, Console) pair for capturing Rich output."""

    def _factory() -> tuple[StringIO, Console]:
        buf = StringIO()
        return buf, Console(file=buf, highlight=False, width=200)

    return _factory
