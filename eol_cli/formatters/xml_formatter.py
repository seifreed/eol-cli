"""XML output formatter."""

import re
import xml.etree.ElementTree as ET
from typing import Any
from xml.dom import minidom


_PLURAL_TO_SINGULAR: dict[str, str] = {
    "releases": "release",
    "tags": "tag",
    "aliases": "alias",
    "identifiers": "identifier",
    "results": "result",
    "products": "product",
    "categories": "category",
    "items": "item",
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


def _dict_to_xml(parent: ET.Element, data: Any, item_name: str = "item") -> None:
    """Convert a dictionary or list to XML elements recursively.

    Args:
        parent: Parent XML element
        data: Data to convert (dict, list, or primitive)
        item_name: Name to use for list items
    """
    if isinstance(data, dict):
        for key, value in data.items():
            safe_key = _sanitize_key(key)
            child = ET.SubElement(parent, safe_key)
            singular = _PLURAL_TO_SINGULAR.get(safe_key, safe_key)
            _dict_to_xml(child, value, item_name=singular)
    elif isinstance(data, list):
        for item in data:
            child = ET.SubElement(parent, item_name)
            _dict_to_xml(child, item, item_name)
    elif data is None:
        parent.text = ""
        parent.set("nil", "true")
    elif isinstance(data, bool):
        parent.text = "true" if data else "false"
    else:
        parent.text = str(data)


def format_xml(data: dict[str, Any], pretty: bool = True) -> str:
    """Format data as XML.

    Args:
        data: Dictionary to format
        pretty: Whether to pretty-print the XML

    Returns:
        Formatted XML string
    """
    root = ET.Element("response")
    _dict_to_xml(root, data)

    if pretty:
        xml_str = ET.tostring(root, encoding="unicode")
        dom = minidom.parseString(xml_str)
        raw = dom.toprettyxml(indent="  ", encoding=None)
        # minidom inserts a blank line after the XML declaration; strip it
        return "\n".join(line for line in raw.splitlines() if line.strip())
    else:
        xml_declaration = '<?xml version="1.0" ?>\n'
        return xml_declaration + ET.tostring(root, encoding="unicode")
