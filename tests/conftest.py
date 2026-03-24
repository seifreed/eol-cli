"""Shared fixtures for eol-cli tests."""

import pytest

from eol_cli.api.client import EOLClient


@pytest.fixture
def client_obj(request: pytest.FixtureRequest) -> dict:
    """Provide a shared EOLClient via Click's obj dict.

    Requires network access. Skips if the requesting test is not marked @pytest.mark.api.
    """
    marker = request.node.get_closest_marker("api")
    if marker is None:
        pytest.skip("Skipping: test requires @pytest.mark.api for network access")
    client = EOLClient()
    yield {"client": client}
    client.close()
