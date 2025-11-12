"""JSON output formatter."""

import json
from typing import Any


def format_json(data: dict[str, Any], indent: int = 2) -> str:
    """Format data as pretty-printed JSON.

    Args:
        data: Dictionary to format
        indent: Number of spaces for indentation

    Returns:
        Formatted JSON string
    """
    return json.dumps(data, indent=indent, ensure_ascii=False)
