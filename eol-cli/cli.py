"""Main CLI entry point for EOL CLI."""

import click
import importlib

# Import version
main_module = importlib.import_module("eol-cli")
__version__ = main_module.__version__

# Import commands
commands = importlib.import_module("eol-cli.commands")
products = commands.products
categories = commands.categories
tags = commands.tags
identifiers = commands.identifiers
index = commands.index


@click.group()
@click.version_option(version=__version__, prog_name="eol-cli")
@click.help_option("-h", "--help")
def main():
    """EOL CLI - Command-line interface for endoflife.date API.
    
    Query end-of-life dates and support lifecycles for various products.
    
    \b
    Examples:
        eol products list               # List all products
        eol products get ubuntu         # Get Ubuntu details
        eol products release python latest  # Get latest Python release
        eol categories get os           # Get all operating systems
        eol tags get database           # Get all database products
        eol identifiers get purl        # Get all PURL identifiers
    
    \b
    For more information:
        GitHub: https://github.com/seifreed/eol-cli
        API:    https://endoflife.date/docs/api/
    """
    pass


# Register command groups
main.add_command(products)
main.add_command(categories)
main.add_command(tags)
main.add_command(identifiers)
main.add_command(index)


if __name__ == "__main__":
    main()

