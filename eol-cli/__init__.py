"""EOL CLI - Command-line interface for endoflife.date API."""

__version__ = "0.1.0"
__author__ = "Marc Rivero"
__email__ = "mriverolopez@gmail.com"
__url__ = "https://github.com/seifreed/eol-cli"

# Note: Due to package name using hyphens, imports need to use importlib
# or users can import directly from submodules
import importlib

def get_client():
    """Get the EOL API client."""
    client_module = importlib.import_module("eol-cli.api.client")
    return client_module.EOLClient

EOLClient = get_client()

__all__ = ["EOLClient", "__version__"]

