# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build, Test, and Lint Commands

```bash
# Install in development mode
pip install -e ".[dev]"

# Run all tests (242 tests with real API calls)
pytest

# Run specific test file
pytest tests/test_api_client.py

# Run with coverage
pytest --cov=eol_cli --cov-report=term-missing

# Run single test
pytest tests/test_cli_commands.py::test_products_get -v

# Format code
black eol_cli/

# Lint
ruff check eol_cli/

# Type check
mypy eol_cli/
```

## Architecture Overview

This is a CLI tool for the [endoflife.date API](https://endoflife.date/docs/api/). The architecture follows a clean separation of concerns:

### Entry Point (`eol_cli/cli.py`)
- Uses Click's `@click.group()` pattern for command groups
- Creates `EOLClient` instance and stores in Click context
- Registers command groups: products, categories, tags, identifiers, index

### API Client (`eol_cli/api/client.py`)
- `EOLClient` class wraps all API endpoints
- Uses `requests.Session` for connection pooling
- Custom exceptions: `EOLAPIError`, `EOLNotFoundError`, `EOLRateLimitError`
- Context manager support (`with EOLClient() as client:`)

### Commands (`eol_cli/commands/`)
- Each module defines a Click command group
- `_output.py` provides shared decorators and `emit()` dispatcher
- Commands use `@format_options` decorator for `--json`, `--xml`, `--sarif` flags
- Output routing: `emit()` dispatches to appropriate formatter based on flags

### Formatters (`eol_cli/formatters/`)
- `rich_formatter.py` - Default terminal output with tables/colors
- `json_formatter.py` - JSON output
- `xml_formatter.py` - XML output
- `sarif_formatter.py` - SARIF v2.1.0 for security tooling integration

### Utilities (`eol_cli/utils/`)
- `fuzzy_search.py` - Provides product name suggestions when not found

## Key Patterns

### Multi-product queries
Products command supports comma-separated names (`ubuntu,python,nodejs`). The `_fetch_products()` helper aggregates results and handles partial failures (some products found, some not).

### Output dispatcher
All commands use `emit(data, output_json, output_xml, rich_fn)` to route output. This ensures consistent format handling across commands.

### Error handling
API errors are caught and converted to Click errors (`click.Abort()`). `EOLNotFoundError` triggers fuzzy suggestions for similar product names.

## Dependencies

Core: `click`, `rich`, `requests`
Dev: `pytest`, `pytest-cov`, `black`, `ruff`, `mypy`

## API Schema Version

Current: `1.2.0` (defined in `eol_cli/api/client.py`)