"""SARIF v2.1.0 output formatter.

Converts endoflife.date API responses into SARIF (Static Analysis Results
Interchange Format) documents. EOL releases produce "error" level results;
active releases produce "note" level results.

Spec: https://docs.oasis-open.org/sarif/sarif/v2.1.0/
"""

import json
from typing import Any

from eol_cli._version import __version__

_SARIF_SCHEMA = (
    "https://docs.oasis-open.org/sarif/sarif/v2.1.0/schemas/sarif-schema-2.1.0.json"
)

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


def _release_to_result(
    product_name: str, release: dict[str, Any]
) -> dict[str, Any]:
    """Convert a single release object into a SARIF result."""
    is_eol = release.get("isEol", False)
    release_cycle = release.get("name", "unknown")
    eol_date = release.get("eolFrom", "N/A")
    prefix = f"{product_name} {release_cycle}" if product_name else release_cycle

    if is_eol:
        level = "error"
        rule_id = _RULE_EOL
        msg = f"{prefix}: End of Life (since {eol_date})"
    else:
        level = "note"
        rule_id = _RULE_ACTIVE
        eol_info = f", EOL scheduled: {eol_date}" if eol_date != "N/A" else ""
        msg = f"{prefix}: Active{eol_info}"

    result: dict[str, Any] = {
        "ruleId": rule_id,
        "level": level,
        "message": {"text": msg},
        "properties": {
            "product": product_name,
            "release": release.get("name", ""),
            "releaseDate": release.get("releaseDate"),
            "isEol": is_eol,
            "eolFrom": release.get("eolFrom"),
            "isLts": release.get("isLts", False),
            "isMaintained": release.get("isMaintained"),
        },
    }
    return result


def _extract_results(data: dict[str, Any]) -> list[dict[str, Any]]:
    """Extract SARIF results from an API response.

    Handles single-product, multi-product, and list responses.
    """
    results: list[dict[str, Any]] = []

    # Multi-product aggregated response
    if "products" in data:
        for product_data in data["products"]:
            results.extend(_extract_results(product_data))
        return results

    # Single product with releases
    result_obj = data.get("result", {})
    if isinstance(result_obj, dict) and "releases" in result_obj:
        product_name = result_obj.get("name", "unknown")
        for release in result_obj["releases"]:
            results.append(_release_to_result(product_name, release))
        return results

    # Single release (from products release command) — no product name in response,
    # so pass empty string to avoid duplicating the release name in the message.
    if isinstance(result_obj, dict) and "isEol" in result_obj:
        results.append(_release_to_result("", result_obj))
        return results

    # List responses (categories, tags, identifiers, index) — no EOL data
    if isinstance(result_obj, list):
        for item in result_obj:
            name = item.get("name", "unknown")
            results.append({
                "ruleId": _RULE_ACTIVE,
                "level": "note",
                "message": {"text": f"{name}: {item.get('uri', '')}"},
                "properties": item,
            })
        return results

    return results


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
