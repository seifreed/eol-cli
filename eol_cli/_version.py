"""Single source of truth for the eol-cli version."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("eol-cli")
except PackageNotFoundError:
    # Fallback for running without pip install -e .
    __version__ = "0.1.0"
