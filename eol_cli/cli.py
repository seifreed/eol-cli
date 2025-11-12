"""Main CLI entry point for EOL CLI."""

import click

from eol_cli import __version__
from eol_cli.commands import categories, identifiers, index, products, tags


@click.group()
@click.version_option(version=__version__, prog_name="eol-cli")
@click.help_option("-h", "--help")
def main():
    """EOL CLI - Command-line interface for endoflife.date API.

    Query end-of-life dates and support lifecycles for various products.

    \b
    Output Formats:
        By default, output is formatted with Rich (colors and tables).
        Use --json or --xml flags on commands to change output format.

    \b
    Examples:
        eol-cli products list               # List all products
        eol-cli products get ubuntu         # Get Ubuntu details (Rich output)
        eol-cli products get ubuntu --json  # Get Ubuntu details (JSON output)
        eol-cli products get ubuntu --xml   # Get Ubuntu details (XML output)
        eol-cli products release python latest  # Get latest Python release
        eol-cli categories get os           # Get all operating systems
        eol-cli tags get database           # Get all database products
        eol-cli identifiers get purl        # Get all PURL identifiers

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
