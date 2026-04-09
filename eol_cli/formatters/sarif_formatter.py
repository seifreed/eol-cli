"""SARIF v2.1.0 output formatter.

Converts endoflife.date API responses into SARIF (Static Analysis Results
Interchange Format) documents. EOL releases produce "error" level results;
active releases produce "note" level results.

Spec: https://docs.oasis-open.org/sarif/sarif/v2.1.0/
"""

import json
from typing import Any

from eol_cli._version import __version__

_SARIF_SCHEMA = "https://docs.oasis-open.org/sarif/sarif/v2.1.0/schemas/sarif-schema-2.1.0.json"

_RULE_EOL = "EOL001"
_RULE_ACTIVE = "EOL002"

_RULES = [
    {
        "id": _RULE_EOL,
        "name": "ProductEndOfLife",
        "shortDescription": {"text": "Product release has reached end of life"},
        "helpUri": "https://endoflife.date",
    },
    {
        "id": _RULE_ACTIVE,
        "name": "ProductActive",
        "shortDescription": {"text": "Product release is actively maintained"},
        "helpUri": "https://endoflife.date",
    },
]


def _build_tool() -> dict[str, Any]:
    """Build the SARIF tool descriptor for eol-cli."""
    return {
        "driver": {
            "name": "eol-cli",
            "version": __version__,
            "informationUri": "https://github.com/seifreed/eol-cli",
            "rules": _RULES,
        }
    }


def _release_to_result(product_name: str, release: dict[str, Any]) -> dict[str, Any]:
    """Convert a single release object into a SARIF result."""
    is_eol = release.get("isEol", False)
    release_cycle = release.get("name", "unknown")
    eol_date = release.get("eolFrom") or "N/A"
    prefix = f"{product_name} {release_cycle}" if product_name else release_cycle

    if is_eol:
        level = "error"
        rule_id = _RULE_EOL
        if eol_date and eol_date != "N/A":
            msg = f"{prefix}: End of Life (since {eol_date})"
        else:
            msg = f"{prefix}: End of Life (date unknown)"
    else:
        level = "note"
        rule_id = _RULE_ACTIVE
        eol_info = f", EOL scheduled: {eol_date}" if eol_date and eol_date != "N/A" else ""
        msg = f"{prefix}: Active{eol_info}"

    result: dict[str, Any] = {
        "ruleId": rule_id,
        "level": level,
        "message": {"text": msg},
        "properties": {
            "product": product_name,
            "release": release.get("name") or "",
            "releaseDate": release.get("releaseDate") or "",
            "isEol": is_eol,
            "eolFrom": release.get("eolFrom") or "",
            "isLts": release.get("isLts") or False,
            "isMaintained": release.get("isMaintained") or False,
        },
    }
    return result


def _extract_products_payload(data: dict[str, Any]) -> list[dict[str, Any]] | None:
    """Extract SARIF results from aggregated multi-product payloads."""
    products = data.get("products")
    if not isinstance(products, list):
        return None

    if not products:
        return []

    results: list[dict[str, Any]] = []
    for product_data in products:
        results.extend(_extract_results(product_data))
    return results


def _extract_single_product_results(data: dict[str, Any]) -> list[dict[str, Any]] | None:
    """Extract SARIF results from a single product response."""
    result_obj = data.get("result")
    if not isinstance(result_obj, dict) or "releases" not in result_obj:
        return None

    product_name = result_obj.get("name", "unknown")
    releases = result_obj.get("releases", [])
    if not isinstance(releases, list):
        return []

    results: list[dict[str, Any]] = []
    for release in releases:
        if isinstance(release, dict):
            results.append(_release_to_result(product_name, release))

    if not releases:
        results.append(
            {
                "ruleId": _RULE_ACTIVE,
                "level": "note",
                "message": {"text": f"{product_name}: No release cycles available"},
                "properties": {"product": product_name, "release": "", "hasReleases": False},
            }
        )
    return results


def _extract_single_release_results(data: dict[str, Any]) -> list[dict[str, Any]] | None:
    """Extract SARIF results from a single release response."""
    result_obj = data.get("result")
    if not isinstance(result_obj, dict) or "isEol" not in result_obj:
        return None

    release_name = result_obj.get("name", "")
    results = [_release_to_result("", result_obj)]
    if release_name:
        results[0]["properties"]["product"] = release_name
    return results


def _extract_list_results(data: dict[str, Any]) -> list[dict[str, Any]] | None:
    """Extract SARIF results from list-like responses."""
    result_obj = data.get("result")
    if not isinstance(result_obj, list):
        return None

    results: list[dict[str, Any]] = []
    for item in result_obj:
        if not isinstance(item, dict):
            name = str(item) if item is not None else "unknown"
            uri = ""
            item = {"value": item}
        else:
            name = item.get("name", "unknown")
            uri = item.get("uri", "")
            if not isinstance(uri, str):
                uri = str(uri)

        item_type = "Item"
        if "/categories/" in uri:
            item_type = "Category"
        elif "/tags/" in uri:
            item_type = "Tag"
        elif "/identifiers/" in uri:
            item_type = "Identifier"

        results.append(
            {
                "ruleId": _RULE_ACTIVE,
                "level": "note",
                "message": {"text": f"{item_type}: {name}" + (f" (URI: {uri})" if uri else "")},
                "properties": item,
            }
        )
    return results


def _extract_results(data: dict[str, Any]) -> list[dict[str, Any]]:
    """Extract SARIF results from an API response."""
    extractors = (
        _extract_products_payload,
        _extract_single_product_results,
        _extract_single_release_results,
        _extract_list_results,
    )

    for extractor in extractors:
        extracted = extractor(data)
        if extracted is not None:
            return extracted

    return []


def format_sarif(data: dict[str, Any]) -> str:
    """Format API response data as a SARIF v2.1.0 document.

    Args:
        data: Dictionary from API response

    Returns:
        SARIF JSON string
    """
    sarif_doc: dict[str, Any] = {
        "version": "2.1.0",
        "$schema": _SARIF_SCHEMA,
        "runs": [
            {
                "tool": _build_tool(),
                "results": _extract_results(data),
            }
        ],
    }
    return json.dumps(sarif_doc, indent=2, ensure_ascii=False)
