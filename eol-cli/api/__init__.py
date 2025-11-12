"""API client module for endoflife.date API."""

import importlib

client_module = importlib.import_module("eol-cli.api.client")
EOLClient = client_module.EOLClient

__all__ = ["EOLClient"]

