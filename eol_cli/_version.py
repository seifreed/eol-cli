"""Version is read from installed package metadata.

The build version is derived from git tags via setuptools-scm when installed.
"""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("eol-cli")
except PackageNotFoundError:
    __version__ = "0.0.0-dev"
