"""Tests for application use cases."""

from typing import cast
from unittest.mock import MagicMock

import pytest

from eol_cli.application import (
    GetCategoryProductsCommand,
    GetIdentifiersByTypeCommand,
    GetIndexCommand,
    GetProductReleaseCommand,
    GetTagProductsCommand,
    ListCategoriesCommand,
    ListIdentifierTypesCommand,
    ListProductsCommand,
    ListTagsCommand,
    OutputFormatCommand,
    OutputMode,
    OutputRenderResult,
    RenderOutputCommand,
    resolve_output_mode,
)
from eol_cli.domain.contracts import ResponseEnvelope
from eol_cli.domain.errors import OutputSelectionError


def test_list_categories_command() -> None:
    gateway = MagicMock()
    gateway.list_categories.return_value = ResponseEnvelope(result=[{"name": "os"}])
    result = ListCategoriesCommand(category_gateway=gateway).run()
    if not (cast(list[dict[str, object]], result.result) == [{"name": "os"}]):
        raise AssertionError
    gateway.list_categories.assert_called_once_with()


def test_get_category_products_command() -> None:
    gateway = MagicMock()
    gateway.get_category_products.return_value = ResponseEnvelope(result=[{"name": "ubuntu"}])
    result = GetCategoryProductsCommand(category_gateway=gateway).run("os")
    products = cast(list[dict[str, object]], result.result)
    if not (products[0]["name"] == "ubuntu"):
        raise AssertionError
    gateway.get_category_products.assert_called_once_with("os")


def test_list_tags_command() -> None:
    gateway = MagicMock()
    gateway.list_tags.return_value = ResponseEnvelope(result=[{"name": "linux"}])
    result = ListTagsCommand(tag_gateway=gateway).run()
    if not (cast(list[dict[str, object]], result.result) == [{"name": "linux"}]):
        raise AssertionError
    gateway.list_tags.assert_called_once_with()


def test_get_tag_products_command() -> None:
    gateway = MagicMock()
    gateway.get_tag_products.return_value = ResponseEnvelope(result=[{"name": "nodejs"}])
    result = GetTagProductsCommand(tag_gateway=gateway).run("linux")
    products = cast(list[dict[str, object]], result.result)
    if not (products[0]["name"] == "nodejs"):
        raise AssertionError
    gateway.get_tag_products.assert_called_once_with("linux")


def test_list_identifier_types_command() -> None:
    gateway = MagicMock()
    gateway.list_identifier_types.return_value = ResponseEnvelope(result=[{"name": "purl"}])
    result = ListIdentifierTypesCommand(identifier_gateway=gateway).run()
    if not (cast(list[dict[str, object]], result.result) == [{"name": "purl"}]):
        raise AssertionError
    gateway.list_identifier_types.assert_called_once_with()


def test_get_identifiers_by_type_command() -> None:
    gateway = MagicMock()
    gateway.get_identifiers_by_type.return_value = ResponseEnvelope(
        result=[{"identifier": "pkg:pypi/..."}]
    )
    result = GetIdentifiersByTypeCommand(identifier_gateway=gateway).run("purl")
    identifiers = cast(list[dict[str, object]], result.result)
    if not (identifiers[0]["identifier"] == "pkg:pypi/..."):
        raise AssertionError
    gateway.get_identifiers_by_type.assert_called_once_with("purl")


def test_get_index_command() -> None:
    gateway = MagicMock()
    gateway.get_index.return_value = ResponseEnvelope(total=2)
    result = GetIndexCommand(index_gateway=gateway).run()
    if not (result.total == 2):
        raise AssertionError
    gateway.get_index.assert_called_once_with()


def test_list_products_command() -> None:
    gateway = MagicMock()
    gateway.list_products.return_value = ResponseEnvelope(result=[])
    result = ListProductsCommand(product_catalog_gateway=gateway).run(full=False)
    if not (cast(list[dict[str, object]], result.result) == []):
        raise AssertionError
    gateway.list_products.assert_called_once_with()
    gateway.list_products_full.assert_not_called()


def test_list_products_command_full() -> None:
    gateway = MagicMock()
    gateway.list_products_full.return_value = ResponseEnvelope(
        result=[{"name": "python", "releases": []}]
    )
    result = ListProductsCommand(product_catalog_gateway=gateway).run(full=True)
    products = cast(list[dict[str, object]], result.result)
    if not (products[0]["name"] == "python"):
        raise AssertionError
    gateway.list_products_full.assert_called_once_with()


def test_product_release_command() -> None:
    gateway = MagicMock()
    gateway.get_product_release.return_value = ResponseEnvelope(result={"name": "3.11"})
    result = GetProductReleaseCommand(product_release_gateway=gateway).run("python", "3.11")
    release = cast(dict[str, object], result.result)
    if not (release["name"] == "3.11"):
        raise AssertionError
    gateway.get_product_release.assert_called_once_with("python", "3.11")


def test_product_release_command_latest() -> None:
    gateway = MagicMock()
    gateway.get_product_latest_release.return_value = ResponseEnvelope(result={"name": "3.13"})
    result = GetProductReleaseCommand(product_release_gateway=gateway).run("python", "latest")
    release = cast(dict[str, object], result.result)
    if not (release["name"] == "3.13"):
        raise AssertionError
    gateway.get_product_latest_release.assert_called_once_with("python")


def test_output_mode_resolver() -> None:
    if resolve_output_mode(False, False, False) is not OutputMode.RICH:
        raise AssertionError
    if resolve_output_mode(True, False, False) is not OutputMode.JSON:
        raise AssertionError
    if resolve_output_mode(False, True, False) is not OutputMode.XML:
        raise AssertionError
    if resolve_output_mode(False, False, True) is not OutputMode.SARIF:
        raise AssertionError


def test_output_mode_resolver_rejects_multiple_formats() -> None:
    with pytest.raises(OutputSelectionError):
        resolve_output_mode(True, True, False)


def test_render_output_command_generates_rich_result_for_rich_mode() -> None:
    command = RenderOutputCommand(
        output_format_command=OutputFormatCommand(
            to_json=lambda data: "json",
            to_xml=lambda data: "xml",
            to_sarif=lambda data: "sarif",
        )
    )
    result = command.run({"key": "value"}, False, False, False)

    if result.mode is not OutputMode.RICH:
        raise AssertionError
    if not (isinstance(result, OutputRenderResult)):
        raise AssertionError
    if not (result.rich_payload == {"key": "value"}):
        raise AssertionError


def test_output_format_command_uses_json_formatter() -> None:
    command = OutputFormatCommand(
        to_json=lambda data: f"json:{data}",
        to_xml=lambda data: "xml",
        to_sarif=lambda data: "sarif",
    )
    mode, payload = command.format_output({}, True, False, False)
    if mode is not OutputMode.JSON:
        raise AssertionError
    if not (payload == "json:{}"):
        raise AssertionError
