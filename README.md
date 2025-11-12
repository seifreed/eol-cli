# EOL CLI

A powerful command-line interface for the [endoflife.date](https://endoflife.date) API. Query end-of-life dates and support lifecycles for various products directly from your terminal.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-176%20passed-brightgreen.svg)](https://github.com/seifreed/eol-cli)
[![Coverage](https://img.shields.io/badge/coverage-99.83%25-brightgreen.svg)](https://github.com/seifreed/eol-cli)

## Features

- 🔍 **Search Products**: List and search all products tracked by endoflife.date
- 📦 **Product Details**: Get detailed information about specific products
- 🏷️ **Categories & Tags**: Filter products by categories and tags
- 🔖 **Identifiers**: Query products by CPE, PURL, and other identifiers
- 📊 **Rich Output**: Beautiful terminal output with tables and colors
- 💾 **JSON Export**: Export data in JSON format for further processing
- 🚀 **Fast & Modular**: Built with Click and designed for extensibility

## Installation

### From PyPI (recommended)

```bash
pip install eol-cli
```

### From Source

```bash
git clone https://github.com/seifreed/eol-cli.git
cd eol-cli
pip install -e .
```

### Development Installation

```bash
git clone https://github.com/seifreed/eol-cli.git
cd eol-cli
pip install -e ".[dev]"
```

## Quick Start

```bash
# List all available products
eol-cli products list

# Get details about a specific product
eol-cli products get ubuntu

# Get latest release information
eol-cli products release ubuntu latest

# List products by category
eol-cli categories get os

# Search products by tag
eol-cli tags get linux

# Export data as JSON
eol-cli products get ubuntu --json
```

## Usage

### Products

```bash
# List all products
eol-cli products list

# List all products with full details
eol-cli products list --full

# Get a specific product (shows only releases table by default)
eol-cli products get <product-name>

# Get multiple products (comma-separated)
eol-cli products get <product1>,<product2>,<product3>

# Get all product details (info, links, identifiers, releases)
eol-cli products get <product-name> --all

# Get a specific release cycle
eol-cli products release <product-name> <release-cycle>

# Get the latest release cycle
eol-cli products release <product-name> latest

# Export as JSON
eol-cli products get ubuntu --json
```

### Categories

```bash
# List all categories
eol-cli categories list

# Get products in a category
eol-cli categories get <category-name>
```

### Tags

```bash
# List all tags
eol-cli tags list

# Get products with a specific tag
eol-cli tags get <tag-name>
```

### Identifiers

```bash
# List all identifier types
eol-cli identifiers list

# Get identifiers by type
eol-cli identifiers get <identifier-type>
```

### API Information

```bash
# Get API index
eol-cli index
```

## Output Formats

### Rich Terminal Output (Default)

By default, the CLI uses Rich to display beautiful, formatted output in your terminal with:
- Color-coded information
- Formatted tables
- Pretty-printed data structures

### JSON Output

Use the `--json` flag to get machine-readable JSON output:

```bash
eol-cli products get ubuntu --json
```

This is useful for:
- Piping to other tools (jq, etc.)
- Scripting and automation
- Integration with other systems

## Examples

### Check if Ubuntu 20.04 is EOL

```bash
eol-cli products release ubuntu 20.04
```

### Find all Linux distributions

```bash
eol-cli tags get linux
```

### Export all products data

```bash
eol-cli products list --full --json > products.json
```

### Check Python versions

```bash
eol-cli products get python
```

### Compare Multiple Products

```bash
# Check multiple products at once
eol-cli products get python,nodejs,ruby

# Export multiple products to JSON
eol-cli products get ubuntu,debian,alpine-linux --json > linux_distros.json

# Compare with XML output
eol-cli products get apache,nginx --xml
```

## Configuration

The CLI uses sensible defaults and requires no configuration. It connects to:
- API Base URL: `https://endoflife.date/api/v1`

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/seifreed/eol-cli.git
cd eol-cli

# Create virtual environment (Python 3.14 recommended)
python3.14 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode with dev dependencies
pip install -e ".[dev]"
```

### Running Tests

The project includes comprehensive unit tests with **99% code coverage** (176 tests, all using real API calls):

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=eol_cli --cov-report=term-missing

# Run with HTML coverage report
pytest --cov=eol_cli --cov-report=html
# Open htmlcov/index.html in your browser

# Run specific test files
pytest tests/test_api_client.py
pytest tests/test_cli_commands.py
pytest tests/test_formatters.py

# Run tests in parallel (faster)
pytest -n auto
```

#### Test Structure

- **test_api_client.py**: Tests for API client functionality (26 tests)
- **test_cli_commands.py**: Tests for CLI commands (47 tests)
- **test_formatters.py**: Tests for JSON, XML, and Rich formatters (27 tests)
- **test_command_error_handling.py**: Tests for error handling and validation (27 tests)
- **test_edge_cases.py**: Tests for edge cases and complex scenarios (26 tests)
- **test_rich_formatter_edge_cases.py**: Tests for Rich formatter edge cases (30 tests)

All tests use **real API calls** to endoflife.date (no mocks or fake data) to ensure accurate behavior.

### Code Formatting

```bash
# Format code with Black
black eol_cli/

# Lint with Ruff
ruff check eol_cli/
```

## Project Structure

```
eol-cli/
├── eol_cli/
│   ├── __init__.py
│   ├── cli.py              # Main CLI entry point
│   ├── api/
│   │   ├── __init__.py
│   │   └── client.py       # API client
│   ├── commands/
│   │   ├── __init__.py
│   │   ├── products.py     # Product commands
│   │   ├── categories.py   # Category commands
│   │   ├── tags.py         # Tag commands
│   │   ├── identifiers.py  # Identifier commands
│   │   └── index.py        # Index command
│   └── formatters/
│       ├── __init__.py
│       ├── json_formatter.py   # JSON output
│       └── rich_formatter.py   # Rich terminal output
├── tests/
├── eol-cli.py              # Wrapper script
├── pyproject.toml
├── setup.py
├── README.md
├── LICENSE
└── .gitignore
```

## Testing

The project maintains a **99.83% code coverage** with comprehensive testing:

### Test Statistics
- **176 tests** - All passing ✅
- **99.83% code coverage** (592/593 lines)
- **Real API calls** - No mocks or fake data
- **2,075 lines** of test code

### Test Suite Overview

| Test File | Tests | Description |
|-----------|-------|-------------|
| `test_api_client.py` | 26 | API client functionality and error handling |
| `test_cli_commands.py` | 47 | CLI command execution and validation |
| `test_formatters.py` | 27 | JSON, XML, and Rich output formatters |
| `test_command_error_handling.py` | 27 | Error handling and exception paths |
| `test_edge_cases.py` | 26 | Edge cases and complex scenarios |
| `test_rich_formatter_edge_cases.py` | 30 | Rich formatter edge cases |

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=eol_cli --cov-report=term-missing

# Run with HTML coverage report
pytest --cov=eol_cli --cov-report=html
# Open htmlcov/index.html in your browser

# Run specific test file
pytest tests/test_api_client.py
```

For detailed testing documentation, see [TESTING.md](TESTING.md).

## API Coverage

This CLI covers all endpoints from the endoflife.date API v1.2.0:

- ✅ Index (`/`)
- ✅ Products (`/products`, `/products/full`, `/products/{product}`)
- ✅ Product Releases (`/products/{product}/releases/{release}`, `/products/{product}/releases/latest`)
- ✅ Categories (`/categories`, `/categories/{category}`)
- ✅ Tags (`/tags`, `/tags/{tag}`)
- ✅ Identifiers (`/identifiers`, `/identifiers/{type}`)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

**Marc Rivero** (@seifreed)
- Email: mriverolopez@gmail.com
- GitHub: [@seifreed](https://github.com/seifreed)

## Support

If you find this project useful, consider supporting its development:

<a href="https://buymeacoffee.com/seifreed" target="_blank">
  <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" >
</a>

Your support helps maintain and improve this project! ☕

## Acknowledgments

- [endoflife.date](https://endoflife.date) for providing the excellent API
