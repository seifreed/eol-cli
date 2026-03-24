"""Version is read from installed package metadata (pyproject.toml is the single source of truth)."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("eol-cli")
except PackageNotFoundError:
    __version__ = "0.0.0-dev"
