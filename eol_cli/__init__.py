"""EOL CLI - Command-line interface for endoflife.date API."""

__version__ = "0.1.0"
__author__ = "Marc Rivero"
__email__ = "mriverolopez@gmail.com"
__url__ = "https://github.com/seifreed/eol-cli"

from eol_cli.api.client import EOLClient

__all__ = ["EOLClient", "__version__"]
