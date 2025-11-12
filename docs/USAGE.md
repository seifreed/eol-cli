# EOL CLI Usage Guide

This guide provides detailed usage instructions and examples for the EOL CLI tool.

## Table of Contents

- [Basic Commands](#basic-commands)
- [Products](#products)
- [Categories](#categories)
- [Tags](#tags)
- [Identifiers](#identifiers)
- [Output Formats](#output-formats)
- [Common Use Cases](#common-use-cases)
- [Tips and Tricks](#tips-and-tricks)

## Basic Commands

### Get Help

```bash
# Main help
eol --help

# Command group help
eol products --help
eol categories --help
eol tags --help
eol identifiers --help

# Specific command help
eol products list --help
eol products get --help
```

### Version

```bash
eol --version
```

## Products

### List All Products

Get a summary of all products:

```bash
eol products list
```

Get full details for all products (includes all release cycles):

```bash
eol products list --full
```

### Get Product Details

Get detailed information about a specific product:

```bash
eol products get python
eol products get ubuntu
eol products get nodejs
eol products get postgresql
```

### Get Release Information

Get information about a specific release cycle:

```bash
eol products release python 3.11
eol products release ubuntu 22.04
eol products release nodejs 20
```

Get the latest release:

```bash
eol products release python latest
eol products release ubuntu latest
eol products release nodejs latest
```

## Categories

### List All Categories

```bash
eol categories list
```

Common categories include:
- `os` - Operating systems
- `app` - Applications
- `framework` - Frameworks
- `lang` - Programming languages
- `database` - Database systems
- `server-app` - Server applications
- `device` - Hardware devices
- `service` - Cloud services
- `standard` - Technical standards

### Get Products by Category

```bash
eol categories get os
eol categories get lang
eol categories get database
eol categories get framework
```

## Tags

### List All Tags

```bash
eol tags list
```

### Get Products by Tag

```bash
eol tags get linux-distribution
eol tags get database
eol tags get google
eol tags get amazon
eol tags get microsoft
```

## Identifiers

### List Identifier Types

```bash
eol identifiers list
```

Common identifier types:
- `purl` - Package URL
- `cpe` - Common Platform Enumeration
- `repology` - Repology identifiers

### Get Identifiers by Type

```bash
eol identifiers get purl
eol identifiers get cpe
eol identifiers get repology
```

## Output Formats

### Rich Terminal Output (Default)

By default, output is formatted with colors and tables for easy reading:

```bash
eol products get python
```

### JSON Output

Use the `--json` flag to get machine-readable JSON:

```bash
eol products get python --json
```

Save JSON output to a file:

```bash
eol products get python --json > python.json
```

Pipe to jq for processing:

```bash
eol products get python --json | jq '.result.releases[0]'
```

## Common Use Cases

### Check if a Product Version is EOL

```bash
# Check Python 3.8
eol products release python 3.8

# Check Ubuntu 20.04
eol products release ubuntu 20.04

# Check Node.js 16
eol products release nodejs 16
```

Look for the "EOL" status in the output. If it shows "EOL (date)", the version is end-of-life.

### Find All Supported Versions of a Product

```bash
eol products get python
```

Look at the release cycles table. Active versions show "Active" status.

### Compare Multiple Products

```bash
# Export to JSON for comparison
eol products get python --json > python.json
eol products get nodejs --json > nodejs.json
eol products get ruby --json > ruby.json
```

### Find Products in Your Stack

Check all web frameworks:

```bash
eol categories get framework
```

Check all databases:

```bash
eol categories get database
```

### Monitor Cloud Services

```bash
eol tags get amazon
eol tags get google
eol tags get microsoft
```

### Export All Products Data

```bash
# Get all products with full details
eol products list --full --json > all_products.json
```

### Check Latest Releases

```bash
# Check latest Python
eol products release python latest

# Check latest Ubuntu
eol products release ubuntu latest

# Check latest PostgreSQL
eol products release postgresql latest
```

## Tips and Tricks

### 1. Use Tab Completion

If your shell supports it, you can enable tab completion for eol commands.

### 2. Combine with Other Tools

```bash
# Count total products
eol products list --json | jq '.total'

# Get all product names
eol products list --json | jq '.result[].name'

# Find products with "python" in the name
eol products list --json | jq '.result[] | select(.name | contains("python"))'
```

### 3. Create Aliases

Add to your `.bashrc` or `.zshrc`:

```bash
alias eol-python="eol products get python"
alias eol-ubuntu="eol products get ubuntu"
alias eol-latest="eol products release"
```

### 4. Check EOL Dates for Your Dependencies

Create a script to check multiple products:

```bash
#!/bin/bash
for product in python nodejs postgresql redis; do
    echo "=== $product ==="
    eol products release $product latest
    echo ""
done
```

### 5. Monitor Your Infrastructure

Export current versions and compare:

```bash
# Save current state
eol products list --json > products_$(date +%Y%m%d).json

# Compare with previous state
diff products_20250101.json products_20250112.json
```

### 6. Quick Product Lookup

```bash
# One-liner to check if a version is EOL
eol products release python 3.8 --json | jq '.result.isEol'
```

### 7. Get Release Dates

```bash
# Get all release dates for a product
eol products get python --json | jq '.result.releases[] | {name: .name, releaseDate: .releaseDate, eolFrom: .eolFrom}'
```

### 8. Filter by Support Status

```bash
# Get only maintained releases
eol products get python --json | jq '.result.releases[] | select(.isMaintained == true)'
```

### 9. Security Monitoring

Check LTS versions:

```bash
eol products get ubuntu --json | jq '.result.releases[] | select(.isLts == true)'
```

### 10. Integration with CI/CD

Use in your CI pipeline to check dependencies:

```bash
# Check if Python version is still supported
if eol products release python 3.8 --json | jq -e '.result.isEol == true' > /dev/null; then
    echo "Warning: Python 3.8 is EOL!"
    exit 1
fi
```

## Error Handling

### Product Not Found

```bash
$ eol products get nonexistent
Error: Product 'nonexistent' not found
Tip: Use 'eol products list' to see available products
```

### Release Not Found

```bash
$ eol products release python 3.99
Error: Release '3.99' not found for product 'python'
Tip: Use 'eol products get python' to see available releases
```

### Rate Limiting

If you see a rate limit error, wait a moment before retrying:

```bash
Error: Rate limit exceeded. Retry after: 60 seconds
```

## Further Reading

- [endoflife.date Website](https://endoflife.date)
- [API Documentation](https://endoflife.date/docs/api/)
- [GitHub Repository](https://github.com/seifreed/eol-cli)
- [OpenAPI Specification](https://github.com/seifreed/eol-cli/blob/main/openapi.yml)

