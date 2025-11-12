.PHONY: help install install-dev test test-cov lint format clean build publish

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install package in production mode
	pip install -e .

install-dev: ## Install package with development dependencies
	pip install -e ".[dev]"

test: ## Run tests
	pytest tests/ -v

test-cov: ## Run tests with coverage report
	pytest tests/ --cov=eol_cli --cov-report=term-missing --cov-report=html

test-fast: ## Run tests without verbose output
	pytest tests/ -q

lint: ## Run linting checks
	@echo "Running ruff..."
	ruff check eol_cli/ tests/
	@echo "Running black check..."
	black --check eol_cli/ tests/
	@echo "All linting checks passed! ✨"

format: ## Format code with black and fix linting issues
	@echo "Formatting code with black..."
	black eol_cli/ tests/
	@echo "Fixing linting issues with ruff..."
	ruff check eol_cli/ tests/ --fix
	@echo "Code formatted! ✨"

type-check: ## Run type checking with mypy
	mypy eol_cli/ --ignore-missing-imports

clean: ## Clean build artifacts and caches
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf coverage.json
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

build: clean ## Build distribution packages
	python -m build

check-all: format lint type-check test ## Run all checks (format, lint, type-check, test)

pre-commit: ## Run pre-commit checks
	pre-commit run --all-files

publish: build ## Publish package to PyPI
	@echo "Publishing to PyPI..."
	twine upload dist/*
	@echo "Published! 🚀"

publish-test: build ## Publish package to TestPyPI
	@echo "Publishing to TestPyPI..."
	twine upload --repository testpypi dist/*
	@echo "Published to TestPyPI! 🧪"

run-dev: ## Run CLI in development mode
	python -m eol_cli.cli

# Development shortcuts
fmt: format ## Alias for format

.DEFAULT_GOAL := help

