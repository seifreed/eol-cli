#!/usr/bin/env python3
"""
EOL CLI - Wrapper script for endoflife.date API

Development convenience wrapper. For installed usage, use the `eol-cli` entry point.

Usage:
    ./eol-cli.py --help
    ./eol-cli.py products list
    ./eol-cli.py products get python
"""

try:
    from eol_cli.cli import main
except ImportError:
    import os
    import sys

    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from eol_cli.cli import main

if __name__ == "__main__":
    main()
