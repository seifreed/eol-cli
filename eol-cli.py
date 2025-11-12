#!/usr/bin/env python3
"""
EOL CLI - Wrapper script for endoflife.date API

This is a convenience wrapper that allows you to run the CLI directly
from the repository without installing it.

Usage:
    ./eol-cli.py --help
    ./eol-cli.py products list
    ./eol-cli.py products get python
    python eol-cli.py products release ubuntu latest
"""

import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run the CLI
from eol_cli.cli import main

if __name__ == "__main__":
    main()
