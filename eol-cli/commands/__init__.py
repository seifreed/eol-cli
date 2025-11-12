"""CLI commands module."""

import importlib

products_module = importlib.import_module("eol-cli.commands.products")
categories_module = importlib.import_module("eol-cli.commands.categories")
tags_module = importlib.import_module("eol-cli.commands.tags")
identifiers_module = importlib.import_module("eol-cli.commands.identifiers")
index_module = importlib.import_module("eol-cli.commands.index")

products = products_module.products
categories = categories_module.categories
tags = tags_module.tags
identifiers = identifiers_module.identifiers
index = index_module.index

__all__ = ["products", "categories", "tags", "identifiers", "index"]

