"""XML output formatter."""

import xml.etree.ElementTree as ET
from typing import Any
from xml.dom import minidom


def _dict_to_xml(parent: ET.Element, data: Any, item_name: str = "item") -> None:
    """Convert a dictionary or list to XML elements recursively.

    Args:
        parent: Parent XML element
        data: Data to convert (dict, list, or primitive)
        item_name: Name to use for list items
    """
    if isinstance(data, dict):
        for key, value in data.items():
            # Handle special characters in key names
            safe_key = str(key).replace(" ", "_").replace("-", "_")
            child = ET.SubElement(parent, safe_key)
            _dict_to_xml(child, value, item_name)
    elif isinstance(data, list):
        for item in data:
            child = ET.SubElement(parent, item_name)
            _dict_to_xml(child, item, item_name)
    elif data is None:
        parent.text = ""
        parent.set("nil", "true")
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
        # Pretty print the XML
        xml_str = ET.tostring(root, encoding="unicode")
        dom = minidom.parseString(xml_str)
        return dom.toprettyxml(indent="  ", encoding=None)
    else:
        return ET.tostring(root, encoding="unicode")
