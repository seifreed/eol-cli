<p align="center">
  <img src="https://img.shields.io/github/v/release/seifreed/eol-cli?label=EOL%20CLI&style=for-the-badge" alt="EOL CLI Release">
</p>

<h1 align="center">EOL CLI</h1>

<p align="center">
  <strong>Query end-of-life dates and support lifecycles from the terminal</strong>
</p>

<p align="center">
  <a href="https://pypi.org/project/eol-cli/"><img src="https://img.shields.io/pypi/v/eol-cli?style=flat-square&logo=pypi&logoColor=white" alt="PyPI Version"></a>
  <a href="https://pypi.org/project/eol-cli/"><img src="https://img.shields.io/pypi/pyversions/eol-cli?style=flat-square&logo=python&logoColor=white" alt="Python Versions"></a>
  <a href="https://github.com/seifreed/eol-cli/blob/main/LICENSE"><img src="https://img.shields.io/github/license/seifreed/eol-cli?style=flat-square" alt="License"></a>
  <a href="https://github.com/seifreed/eol-cli/actions"><img src="https://img.shields.io/github/actions/workflow/status/seifreed/eol-cli/test.yml?branch=main&style=flat-square&logo=github&label=CI" alt="CI Status"></a>
</p>

<p align="center">
  <a href="https://github.com/seifreed/eol-cli/stargazers"><img src="https://img.shields.io/github/stars/seifreed/eol-cli?style=flat-square" alt="GitHub Stars"></a>
  <a href="https://github.com/seifreed/eol-cli/issues"><img src="https://img.shields.io/github/issues/seifreed/eol-cli?style=flat-square" alt="GitHub Issues"></a>
  <a href="https://github.com/seifreed/eol-cli/releases"><img src="https://img.shields.io/github/v/release/seifreed/eol-cli?style=flat-square" alt="GitHub Release"></a>
</p>

---

## Overview

**EOL CLI** is a Python command-line tool for querying the [endoflife.date](https://endoflife.date) API. It helps you inspect product lifecycles, release cycles, categories, tags, identifiers, and API metadata directly from your terminal.

### Key Features

| Feature | Description |
|---------|-------------|
| **Product Lookup** | Inspect products, release cycles, and release metadata |
| **Category Queries** | List categories or fetch products by category |
| **Tag Queries** | List tags or fetch products by tag |
| **Identifier Queries** | Resolve products by PURL, CPE, and other identifier types |
| **API Index** | Inspect the API index and available surfaces |
| **Rich Output** | Human-friendly terminal output with tables and colors |
| **Structured Output** | JSON, XML, and SARIF output for automation |
| **Tag-Based Releases** | Publish releases from git tags with GitHub Actions |

### Supported Commands

| Command | Purpose |
|---------|---------|
| `products list` | List all products |
| `products get <name>` | Show product details |
| `products release <product> <release>` | Show a specific release cycle |
| `categories list` | List categories |
| `categories get <name>` | Show products in a category |
| `tags list` | List tags |
| `tags get <name>` | Show products for a tag |
| `identifiers list` | List identifier types |
| `identifiers get <type>` | Show products for an identifier type |
| `index` | Show API index data |

---

## Installation

### From PyPI

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

---

## Quick Start

```bash
# List all available products
eol-cli products list

# Get details for a specific product
eol-cli products get ubuntu

# Get the latest release information
eol-cli products release python latest

# Query products by category
eol-cli categories get os

# Query products by tag
eol-cli tags get linux
```

---

## Usage

### Products

```bash
# List all products
eol-cli products list

# List all products with full details
eol-cli products list --full

# Get a specific product
eol-cli products get <product-name>

# Get multiple products (comma-separated)
eol-cli products get <product1>,<product2>,<product3>

# Get all product details
eol-cli products get <product-name> --all

# Get a specific release cycle
eol-cli products release <product-name> <release-cycle>

# Get the latest release cycle
eol-cli products release <product-name> latest
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

# Get products by identifier type
eol-cli identifiers get <identifier-type>
```

### API Information

```bash
# Get API index
eol-cli index
```

---

## Output Formats

### Rich Terminal Output

Rich is the default output format. It renders tables and summaries that are easy to read in a terminal.

### JSON Output

Use `--json` for machine-readable JSON output.

```bash
eol-cli products get ubuntu --json
```

### XML Output

Use `--xml` for XML output.

```bash
eol-cli products get ubuntu --xml
```

### SARIF Output

Use `--sarif` for SARIF output in security and automation workflows.

```bash
eol-cli products get ubuntu --sarif
```

---

## Releases

Releases are published from version tags.

```bash
git tag v0.1.0
git push origin v0.1.0
```

That workflow:
- Builds the package artifacts
- Publishes to PyPI with GitHub Actions OIDC trusted publishing
- Uploads the built files to the GitHub Release assets

Before using the first release, configure PyPI trusted publishing for this repository:
- Owner: `seifreed`
- Repository: `eol-cli`
- Workflow file: `publish.yml`
- Environment: `pypi`

---

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/seifreed/eol-cli.git
cd eol-cli

# Create a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install development dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
pytest

# Run tests without API calls
pytest -q -m "not api" --tb=short

# Run with coverage
pytest --cov=eol_cli --cov-report=term-missing
```

### Code Quality

```bash
# Lint
ruff check eol_cli tests

# Format check
black --check eol_cli tests

# Type check
mypy eol_cli tests
```

---

## Requirements

- Python 3.13 or 3.14
- See [pyproject.toml](pyproject.toml) for the full dependency list

---

## Contributing

Contributions are welcome.

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push the branch
5. Open a pull request

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

**Attribution**
- Author: Marc Rivero
- Repository: [github.com/seifreed/eol-cli](https://github.com/seifreed/eol-cli)

---

<p align="center">
  <sub>Built for clean EOL lookups and release automation.</sub>
</p>
