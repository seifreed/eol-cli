"""XML output formatter."""

import re
from typing import Any

_PLURAL_TO_SINGULAR: dict[str, str] = {
    "releases": "release",
    "tags": "tag",
    "aliases": "alias",
    "identifiers": "identifier",
    "results": "result",
    "products": "product",
    "categories": "category",
    "items": "item",
    "links": "link",
    "cycles": "cycle",
    "versions": "version",
}

# XML element names must start with a letter or underscore, and contain only
# letters, digits, hyphens, underscores, and periods.
_INVALID_START = re.compile(r"^[^a-zA-Z_]")
_INVALID_CHARS = re.compile(r"[^a-zA-Z0-9._-]")


def _sanitize_key(key: str) -> str:
    """Sanitize a dict key into a valid XML element name."""
    safe = _INVALID_CHARS.sub("_", str(key))
    if _INVALID_START.match(safe):
        safe = f"_{safe}"
    return safe


def _escape_xml(text: str) -> str:
    """Escape XML special characters in text nodes."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def _xml_lines(
    name: str, data: Any, item_name: str = "item", level: int = 0, pretty: bool = True
) -> list[str]:
    """Convert a dictionary, list, or primitive into XML lines."""
    indent = ("  " * level) if pretty else ""
    if isinstance(data, dict):
        dict_lines = [f"{indent}<{name}>"]
        for key, value in data.items():
            safe_key = _sanitize_key(key)
            singular = _PLURAL_TO_SINGULAR.get(safe_key, safe_key)
            dict_lines.extend(
                _xml_lines(safe_key, value, item_name=singular, level=level + 1, pretty=pretty)
            )
        dict_lines.append(f"{indent}</{name}>")
        return dict_lines

    if isinstance(data, list):
        item_lines: list[str] = [f"{indent}<{name}>"]
        for item in data:
            item_lines.extend(
                _xml_lines(item_name, item, item_name=item_name, level=level + 1, pretty=pretty)
            )
        item_lines.append(f"{indent}</{name}>")
        return item_lines

    if data is None:
        return [f'{indent}<{name} nil="true" />']

    if isinstance(data, bool):
        text = "true" if data else "false"
    else:
        text = _escape_xml(str(data))

    return [f"{indent}<{name}>{text}</{name}>"]


def format_xml(data: dict[str, Any], pretty: bool = True) -> str:
    """Format data as XML.

    Args:
        data: Dictionary to format
        pretty: Whether to pretty-print the XML

    Returns:
        Formatted XML string
    """
    body = _xml_lines("response", data, level=0, pretty=pretty)
    xml_declaration = '<?xml version="1.0" ?>'
    if pretty:
        return xml_declaration + "\n" + "\n".join(body)
    return xml_declaration + "".join(body)
